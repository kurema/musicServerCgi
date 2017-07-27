#!/usr/local/bin/perl
use utf8;
use Encode;
use strict;
use File::Spec;
use File::Basename;
use File::Find;
use JSON;
use open IO => qw/ :encoding(utf8) :std /;

require DBD::SQLite;
require DBI;

require "commonm.pl";

my %conf=GetConf(File::Spec->catfile(dirname(__FILE__),"music.conf"));
my $music_exts=$conf{"musicexts"};

my $dbh = DBI->connect("dbi:SQLite:dbname=".$conf{"sqlitedb"});

$dbh->{sqlite_unicode} = 1;
#$dbh->do("set names utf8");

$dbh->do("drop table album;");
$dbh->do("drop table song;");
$dbh->do("drop table artist;");


$dbh->do("create table album(id,filename,title,artistid,tracks,genre);");
$dbh->do("create table song(id,filename,albumid,track,title,format,artistid,duration);");
$dbh->do("create table artist(id,name);");

my $id=0;
my %albumIDs;
my $albumID=0;
my %artistIDs;
my $artistID=0;
find(\&processFile,$conf{"songhome"});
$dbh->disconnect;

sub processFile{
#if($id==30){$dbh->disconnect;exit;}

my $file=$File::Find::name;
if(! -e $file){return;}
if(-d $file){return;}
my ($ext)=$file=~ /(\.[^\.]+)$/;
if($ext ne "" && index($music_exts,$ext)>=0){


my $songinfo=getJsonInfo($file);
my $tags=$songinfo->{"format"}->{"tags"};

my ($albumartistf,$albumf,$trackf,$songtitlef)= $file=~ /\/([^\/]+?) \- ([^\/]+)\/(\d+)\.\s?([^\/]+)\.([^\/\.]+)$/;
my ($albumartist,$album,$track,$songtitle,$albumtrack,$artist,$genre)=(getLastTag($tags->{"album_artist"}),getLastTag($tags->{"ALBUM"}),$tags->{"track"},getLastTag($tags->{"TITLE"}),$tags->{"TOTALTRACKS"},getLastTag($tags->{"ARTIST"}),getLastTag($tags->{"GENRE"}));
if($albumartist eq ""){$albumartist=$artist;}

my $albumIDTemp=0;
if(defined($albumIDs{$album})){$albumIDTemp=$albumIDs{$album};}else{
$albumID++;
$dbh->do(("insert into album(id,filename,title,artistid,tracks,genre) values($albumID,'".escape_sql(decode_utf8($File::Find::dir))."','".escape_sql($album)."',".getArtistId($albumartist).",'".escape_sql($albumtrack)."','".escape_sql($genre)."');"));
$albumIDs{$album}=$albumID;
$albumIDTemp=$albumID;
print "album:$album by $albumartistf\n";
}

$dbh->do(("insert into song (id,filename,albumid,track,title,format,artistid,duration) values($id,'".escape_sql(decode_utf8($file))."',$albumIDTemp,".escape_sql($track).",'".escape_sql($songtitle)."','".escape_sql($ext)."',".getArtistId($artist).",'".$songinfo->{"format"}->{"duration"}."');"));
$id++;
print "$track. $songtitle by $artist\n";
}
}

sub getArtistId{
my ($artistarg)=@_;
my $artistIDTemp;
if(defined($artistIDs{$artistarg})){$artistIDTemp=$artistIDs{$artistarg};}else{
$artistID++;
$dbh->do(("insert into artist(id,name) values($artistID,'".escape_sql($artistarg)."');"));
$artistIDs{$artistarg}=$artistID;
$artistIDTemp=$artistID;
}
return $artistIDTemp;
}

sub getLastTag{
my ($arg)=@_;
my @rep=split(/;/,$arg);
return @rep[$#rep];
}

sub getJsonInfo{
my ($file)=@_;
open INFO ,"ffprobe -v quiet -print_format json -show_format \"".escape_bash_in_dq($file)."\" |";
#binmode INFO,":utf8";
local $/ = undef;
my $data = <INFO>;
close(INFO);
return from_json($data);
}

sub escape_sql{
  my $str=$_[0];
  if(defined($str)){
    $str=~ s/\\/\\\\\\\\/go;
    $str=~ s/'/''/go;
    $str=~ s/%/\\\\%/go;
    $str=~ s/_/\\\\_/go;
  }
  return $str;
}

sub escape_bash_in_dq{
  my $str=$_[0];
  if(defined($str)){
    $str=~ s/\\/\\\\/go;
    $str=~ s/\"/\\\"/go;
    $str=~ s/\`/\\\`/go;
    $str=~ s/\$/\\\$/go;
  }
  return $str;
}
