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
my @pathInfo = split("/", substr($q->path_info(),1));

print "Content-Type: application/json;charset=utf-8;\n\n";

if($pathInfo[0] eq "album"){
my %hash=("id"=>"Id","title"=>"Title","artistid"=>"ArtistID","tracks"=>"Tracks","thumbexist"=>"ThumbExist","genre"=>"Genre");
if($pathInfo[1] eq "artist"){
OutputJson($pathInfo[2],$dbh,\%hash,"album","artistid");
}else{
OutputJson($pathInfo[1],$dbh,\%hash,"album");
}
}elsif($pathInfo[0] eq "song"){
my %hash=("id"=>"Id","albumid"=>"AlbumId","track"=>"Track","title"=>"Title","format"=>"Format","artistid"=>"ArtistID","duration"=>"Duration");
if($pathInfo[1] eq "album"){
OutputJson($pathInfo[2],$dbh,\%hash,"song","albumid");
}elsif($pathInfo[1] eq "artist"){
OutputJson($pathInfo[2],$dbh,\%hash,"song","artistid");
}else{
OutputJson($pathInfo[1],$dbh,\%hash,"song");
}
}elsif($pathInfo[0] eq "artist"){
my %hash=("id"=>"Id","name"=>"Name");
OutputJson($pathInfo[1],$dbh,\%hash,"artist");
}
$dbh->disconnect;

sub OutputJson{
my $idRange=$_[0];
my $dbh=$_[1];
my $jsonKeyRef=$_[2];
my %jsonKey=%$jsonKeyRef;
my $tablename=$_[3];
my $targetKey=$_[4]ne""?$_[4]:"id";

my $sth;

if($idRange eq ""){
$sth=$dbh->prepare("select * from ".$tablename);
$sth->execute;
}elsif($idRange=~ m/^(\d+)\-(\d+)$/){
my $min=$1<$2?$1:$2;
my $max=$1<$2?$2:$1;

$sth=$dbh->prepare("select * from ".$tablename." where $targetKey >= ".$min." AND $targetKey<= ".$max);
$sth->execute;
}elsif($idRange=~ m/^(\d+)$/){
$sth=$dbh->prepare("select * from ".$tablename." where $targetKey = ".$1);
$sth->execute;
}else{return;}
print "[ ";
my $first1=1;
while(my $info=$sth->fetchrow_hashref()){
if($first1!=1){print ",\n";}else{$first1=0;}
my $first2=1;
print "{\n";
foreach my $key (keys %jsonKey){
if($first2!=1){print ",\n";}else{$first2=0;}
print " \"".$jsonKey{$key}."\" : \"".EscapeJson($info->{$key})."\"";
}
print "\n}";
}
$sth->finish;
print "\n]";
}

sub EscapeJson{
my $text=$_[0];
$text=~ s/([\\\"])/\\$1/g;
return $text;
}
