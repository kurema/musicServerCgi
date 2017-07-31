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
if($format eq "" || ! defined($format)){
TransferFile($info[1]);
}else{
if($format eq "wav"){
TranscodeFile($info[1],"wav","audio/wav",$from);
}elsif($format eq "mp3"){
TranscodeFile($info[1],"mp3","audio/mp3",$from);
}elsif($format eq "ogg"){
TranscodeFile($info[1],"ogg","audio/ogg",$from);
}elsif($format eq "m4a"){
TranscodeFile($info[1],"m4a","audio/m4a",$from);
}
}

sub TranscodeFile{
my ($file,$ext,$mimetype,$from)=@_;
my $option="";
if($from ne "" && defined($from)){
  if($from=~ m/(\d+\.?\d*)/){
    $option.="-ss ".$1." ";
  }
}
print "Content-Type: $mimetype\n\n";
open AUDIO,"ffmpeg $option -i \"$file\" -loglevel quiet pipe:1.$ext|";
while (read AUDIO, my $buffer, 4096){
print $buffer;
}
}
