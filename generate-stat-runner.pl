#!/usr/bin/env perl
use strict;
use utf8;
use threads;
use POSIX;
use Getopt::Long;
use List::Util qw(sum min max shuffle);
binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my ($PREFIX,$DATABASE_DIR,$SICSTUS_LOCATION,$GEOQUERY_LOCATION,$LETRAC,$REF,$OUTPUT, $KEEP_SPLIT);
my $LETRAC=".";
my $THREADS=28;
my $TUNE_FACTOR=0;
GetOptions(
    "prefix=s" => \$PREFIX,
	"sicstus-dir=s" => \$SICSTUS_LOCATION,
	"geoquery-dir=s" => \$GEOQUERY_LOCATION,
	"letrac-dir=s"=> \$LETRAC,
	"ref=s"=> \$REF,
	"output=s" => \$OUTPUT,
    "tune-factor=i" => \$TUNE_FACTOR,
    "threads=s"=> \$THREADS,
    "database-dir=s" => \$DATABASE_DIR, 
    "keep-split!" => \$KEEP_SPLIT,
);

my $lines=0;
open(FH,"$PREFIX.uniq") or die "$!";
$lines++ while <FH>;
close FH;

safesystem("$LETRAC/script/tune/qdatabase.py $DATABASE_DIR") if $DATABASE_DIR;
my $database_cmd = $DATABASE_DIR ? " --database $DATABASE_DIR" : "";
my $lines=int(ceil($lines/$THREADS));
my $split_dir = "$PREFIX\_split";
safesystem("rm -rf $split_dir") if (-d $split_dir);
safesystem("mkdir $split_dir") or die;
safesystem("$LETRAC/script/tune/split_factor.py $TUNE_FACTOR $PREFIX.uniq > $PREFIX.uniq.factor 2> $PREFIX.paraphrase");
safesystem("split $PREFIX.uniq.factor -l $lines $split_dir/file -d") or die;
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
for my $data (qw(qdata reduct n geoquery.log semout semout.sync query)) {
    safesystem("cat $split_dir/file*.$data > $PREFIX.$data");
}
if (not $KEEP_SPLIT) {
    safesystem("rm -rf $split_dir");
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
    safesystem("$LETRAC/script/tune/generate_query_data.py --input $dir.reduct --geoquery_dir $GEOQUERY_LOCATION --output $dir.query$database_cmd")or die;
    sleep(0.1);
    safesystem("cat $dir.query | $SICSTUS_LOCATION/bin/sicstus 2> $dir.geoquery.log | awk 'NF' > $dir.semout") or die;
    sleep(0.1);
    safesystem("$LETRAC/script/tune/synchronize_semantic_output.py --log_file $dir.geoquery.log --output $dir.semout --sync $dir.qsync$database_cmd > $dir.semout.sync") or die;
    print STDERR "$dir execution is done.\n";
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
