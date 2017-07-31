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
$dbh->{sqlite_unicode} = 1;

my $q = new CGI;
my ($id) = $q->param('id')=~ m/(\d+)/;
if($id eq "" || ! defined($id)){exit;}

my $sth=$dbh->prepare("select * from album where id =".$id);
$sth->execute;
my $info=$sth->fetchrow_hashref;
$sth->finish;

if($info->{"filename"} eq ""){exit;}
my @files=glob('"'.File::Spec->catfile($info->{"filename"},"*").'"');
my $minsize=$conf{"thumbmax"};
my $minsizeFile="";
foreach my $file (@files){
my ($ext) = $file=~ m/(\.[^\.]+$)/;
if(index($conf{"thumbexts"},$ext)>=0){
if((-s $file)<$minsize){$minsize=-s $file;$minsizeFile=$file;}
}
}
if($minsizeFile ne ""){
$dbh->disconnect;
TransferFile($minsizeFile);
}else{
$dbh->disconnect;
print "Status: 404 Not Found\n\n";
}

#sub TransferResize{
#my $file=$_[0];
#my $size=$_[1];
#my $image = Image::Resize->new($file);
#my $gd = $image->resize($size, $size);
#
#print "Content-Type: image/jpeg\n\n";
#print $gd->jpeg();
#}
