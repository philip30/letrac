#!/usr/bin/perl
use strict;
use utf8;
use threads;
use Getopt::Long;
use List::Util qw(sum min max shuffle);
binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my ($PREFIX,$SICSTUS_LOCATION,$GEOQUERY_LOCATION,$LETRAC,$REF,$OUTPUT);
my $LETRAC=".";
my $THREADS=28;

GetOptions(
    "prefix=s" => \$PREFIX,
	"sicstus-dir=s" => \$SICSTUS_LOCATION,
	"geoquery-dir=s" => \$GEOQUERY_LOCATION,
	"letrac-dir=s"=> \$LETRAC,
	"ref=s"=> \$REF,
	"output=s" => \$OUTPUT,
    "threads=s"=> \$THREADS,
);

my $lines=0;
open(FH,"$PREFIX.uniq") or die "$!";
$lines++ while <FH>;
close FH;

my $lines=int($lines/$THREADS);
my $split_dir = "$PREFIX\_split";
safesystem("rm -rf $split_dir") if (-d $split_dir);
safesystem("mkdir $split_dir") or die;
safesystem("split $PREFIX.uniq -l $lines $split_dir/file -d") or die;
safesystem("ls $split_dir");
sleep(0.5);
# MAP
opendir(DIR,$split_dir) or die $!;
my @dots = grep {-f "$split_dir/$_" } readdir(DIR);
my @all_threads = ();
foreach my $file (sort(@dots)) {
    my $file_name="$split_dir/$file";
    my $thread=threads->create(\&stat_gen, $file_name);
    push (@all_threads,$thread);
}
foreach my $thread (@all_threads) {
    $thread->join();
}
closedir(DIR);

# REDUCE
for my $data (qw(qdata reduct n geoquery.log semout semout.sync)) {
    safesystem("cat $split_dir/file*.$data > $PREFIX.$data");
}
safesystem("$LETRAC/script/tune/generate_stat_data.py --gs $REF --semout $PREFIX.semout.sync --n $PREFIX.n > $OUTPUT") or die;

# Auxiliary functions
sub stat_gen {
    my $dir = shift;
    my $ctr=0;
    while (not (-r $dir and -e $dir) and $ctr < 10) {
        sleep(1);
        ++$ctr;
    }
    die "Cannot open file $dir" if $ctr == 10;
    safesystem("$LETRAC/script/tune/split_query_data.py < $dir > $dir.qdata 2> $dir.n") or die;
    sleep(0.1);
    safesystem("$LETRAC/script/tune/breduct.py --alphabet < $dir.qdata > $dir.reduct") or die;
    sleep(0.1);
    safesystem("$LETRAC/script/tune/generate_query_data.py $dir.reduct $GEOQUERY_LOCATION $dir.query")or die;
    sleep(0.1);
    safesystem("cat $dir.query | $SICSTUS_LOCATION/bin/sicstus 2> $dir.geoquery.log | awk 'NF' > $dir.semout") or die;
    sleep(0.1);
    safesystem("$LETRAC/script/tune/synchronize_semantic_output.py $dir.geoquery.log $dir.semout > $dir.semout.sync") or die;
}


sub safesystem {
  print STDERR "Executing: @_\n";
  system(@_);
  if ($? == -1) {
      warn "Failed to execute: @_\n  $!";
      exit(1);
  } elsif ($? & 127) {
      printf STDERR "Execution of: @_\n  died with signal %d, %s coredump\n",
          ($? & 127),  ($? & 128) ? 'with' : 'without';
      exit(1);
  } else {
    my $exitcode = $? >> 8;
    warn "Exit code: $exitcode\n" if $exitcode;
    return ! $exitcode;
  }
}
