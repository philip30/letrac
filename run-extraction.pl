#!/usr/bin/env perl
# Script to perform Lexical Acquisition
# Philip Arthur

use strict;
use utf8;
use Getopt::Long;
use List::Util qw(sum min max shuffle);
binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my ($PIALIGN_DIR, $WORKING_DIR, $INPUT, $MERGE_UNARY, $LETRAC_DIR, $FORCE, $VERBOSE, $LAST_STEP);
my ($THREE_SYNC, $MAX_SIZE,$ALIGN,$MANUAL);
my $MAX_SIZE = "4";

GetOptions(
    # Necessary
    "letrac=s" => \$LETRAC_DIR,
    "pialign=s" => \$PIALIGN_DIR,
    "working-dir=s" => \$WORKING_DIR,
    "input-file=s" => \$INPUT,
    # Option
    "last-step=s" => \$LAST_STEP,
    "verbose!" => \$VERBOSE,
    "merge-unary!" => \$MERGE_UNARY,
    "max-size=s" => \$MAX_SIZE,
    "force!" => \$FORCE,
    "align=s" => \$ALIGN,
    "manual=s" => \$MANUAL,
);

if (not (defined($LETRAC_DIR) && defined($PIALIGN_DIR) && defined($WORKING_DIR) && defined($INPUT))) {
    die "Usage: run-extraction.pl -letrac-dir [LETRAC] -pialign-dir [PIALIGN] -working-dir [WORKING DIR] -input-file [INPUT_FILE]\n";
}

### START HERE
my $file_name = substr($INPUT, rindex($INPUT, '/')+1);

# CREATING DIR
if (not (mkdir $WORKING_DIR)) {
    if ($FORCE) {
        safesystem("rm -rf $WORKING_DIR");
        safesystem("mkdir $WORKING_DIR");
    } else {
        die "couldn't mkdir $WORKING_DIR, directory exists.";
    }
} 

safesystem("mkdir $WORKING_DIR/data");
# Preparing input for alignment
safesystem("$LETRAC_DIR/script/extract/input_preprocess.py < $INPUT > $WORKING_DIR/data/$file_name.preprocess");

# Creating input for alignment
my $manual = $MANUAL ? " --manual $MANUAL" : "";
safesystem("$LETRAC_DIR/script/extract/align-gen.py$manual --osent $WORKING_DIR/data/$file_name.sent --ologic $WORKING_DIR/data/$file_name.fol --input $WORKING_DIR/data/$file_name.preprocess") or die "Failed on creating input for alignment";
safesystem("$LETRAC_DIR/script/extract/swr.py < $WORKING_DIR/data/$file_name.sent > $WORKING_DIR/data/$file_name.kword") if ($THREE_SYNC);
exit(0) if $LAST_STEP eq "input";

# Running Alignment
safesystem("mkdir $WORKING_DIR/align");
if (not $ALIGN) {
    $ALIGN = "$WORKING_DIR/align/align.txt";
    safesystem("$PIALIGN_DIR/src/bin/pialign $WORKING_DIR/data/$file_name.sent.gin $WORKING_DIR/data/$file_name.fol.gin $WORKING_DIR/align/align-out. 2> $WORKING_DIR/align/pialign-log.txt") or die "Failed on running alignment";
    safesystem("$PIALIGN_DIR/script/itgstats.pl talign < $WORKING_DIR/align/align-out.1.samp > $ALIGN") or die "Failed on combining alignment";
} 

# Visualizing alignment
safesystem("head -\$(wc -l $WORKING_DIR/data/$file_name.sent) $WORKING_DIR/data/$file_name.fol.gin > $WORKING_DIR/data/$file_name.fol.visin");
safesystem("$LETRAC_DIR/script/extract/visualize.pl $WORKING_DIR/data/$file_name.sent $WORKING_DIR/data/$file_name.fol.visin $ALIGN 2 1 > $WORKING_DIR/align/align.vis");
exit(0) if $LAST_STEP eq "align"; 

safesystem("mkdir $WORKING_DIR/model");
# lexical-acquisition
my $lex_command = "$LETRAC_DIR/script/extract/lexical-acq.py --input $WORKING_DIR/data/$file_name.preprocess --sent $WORKING_DIR/data/$file_name.sent --fol $WORKING_DIR/data/$file_name.fol --align $ALIGN --max_size $MAX_SIZE";
$lex_command .= " --verbose" if $VERBOSE;
$lex_command .= " --merge_unary" if $MERGE_UNARY;
$lex_command .= " > $WORKING_DIR/model/lexical-grammar.txt";
safesystem($lex_command);

# Auxiliary functions
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
