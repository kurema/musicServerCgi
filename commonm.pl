use File::MimeInfo qw(globs);
use Digest::MD5 qw/md5_hex/;
use strict;

sub GetConf{
  my $file=$_[0];
  open(CONF,"< $file");
  my %result;
  while(my $line=<CONF>){
    if($line =~ m/^\#/){ next;}
    if($line =~ m/^(\w+)\=(.+)$/){
      $result{$1}=$2;
      next;
    }
  }
  return %result;
}


sub TransferFile{
  my $file=$_[0];
  my ($ext)= $file =~ m!\.([^\.]+)$!;

  my $blocksize=4096;

  my $mimetype=globs($file);
  my $filesize=-s $file;

  open MOVIE, "<" , $file or die;
  binmode MOVIE;

  my $range=$ENV{'HTTP_RANGE'};
print <<"HEAD";
Content-type: $mimetype
Accept-Ranges: bytes
HEAD
print "Etag: \"". md5_hex($ENV{"REQUEST_URI"}) ."$filesize\"\n";

  if($range ne ""){
    my ($start,$end)= $range=~ m/(\d*)\-(\d*)/;
    if ($start eq "" || $start>$filesize){$start=0;}
    if ($end eq "" || $end<=$start){$end=$filesize-1;}
    my $length=$end-$start+1;

print <<"HEAD";
Status: 206 Partial Content
Content-Length: $length
Content-Range: bytes $start-$end/$filesize
HEAD

    binmode STDOUT;
    seek MOVIE, $start,0;
    my $current=$start;

    while (read MOVIE, my $buffer, ($end-$current+1<$blocksize?$end-$current+1:$blocksize)){
      print $buffer;
      $current+=$blocksize;
      if($end<=$current){return;}
    }
  }else{
    print "Content-Length: $filesize\n\n";
    binmode STDOUT;

    while (read MOVIE, my $buffer, $blocksize){
      print $buffer;
    }
  }
}

1;
