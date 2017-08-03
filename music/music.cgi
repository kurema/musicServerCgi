#!/usr/bin/perl
use strict;
use File::Spec;
use File::Basename;
use CGI;

require DBD::SQLite;
require DBI;

require File::Spec->catfile(dirname(__FILE__),"commonm.pl");


my %conf=GetConf(File::Spec->catfile(dirname(__FILE__),"music.conf"));

my $dbh = DBI->connect("dbi:SQLite:dbname=".$conf{"sqlitedb"});

my $q = new CGI;
my ($id) = $q->param('id')=~ m/(\d+)/;
#print "Content-Type: text/html\n\n";
if($id eq "" || ! defined($id)){exit;}
my $sth=$dbh->prepare("select * from song where id =".$id);
$sth->execute;
my @info=$sth->fetchrow_array;
$sth->finish;
$dbh->disconnect;

my $from=$q->param('from');
my $format=$q->param('f');
my ($kbps)= $q->param('kbps')=~ m/(\d+)/;

if($format eq "" || ! defined($format)){
TransferFile($info[1]);
}else{
if($format eq "wav"){
TranscodeFile($info[1],"wav","pcm_s16le","audio/wav",$from);
}elsif($format eq "mp3"){
TranscodeFile($info[1],"mp3","libmp3lame","audio/mp3",$from,$kbps);
}elsif($format eq "ogg"){
TranscodeFile($info[1],"ogg","libvorbis","audio/ogg",$from,$kbps);
}elsif($format eq "m4a"){
TranscodeFile($info[1],"m4a","libfaac","audio/m4a",$from,$kbps);
}
}

sub TranscodeFile{
my ($file,$ext,$acodec,$mimetype,$from,$kbps)=@_;
my $option="";
my $option2="";
if($from ne "" && defined($from)){
  if($from=~ m/(\d+\.?\d*)/){
    $option.="-ss ".$1." ";
  }
}
if(defined($kbps) && $kbps ne ""){
  $option2.="-ab ".$kbps."k ";
}
my $command="ffmpeg $option -i \"".EscapeShell($file)."\" -vn $option2 -acodec $acodec -loglevel quiet pipe:1.$ext";
#print $command;exit;
print "Content-Type: $mimetype\n\n";
open AUDIO,"$command|";
binmode(AUDIO);
while (read AUDIO, my $buffer, 4096){
print $buffer;
}
}

sub EscapeShell{
my $word=$_[0];
$word=~ s/\\/\\\\/g;
$word=~ s/\$/\\\$/g;
$word=~ s/\`/\\\`/g;
$word=~ s/\"/\\\"/g;
return $word;
}
