#!/usr/bin/env perl

use strict;
use utf8;
use Getopt::Long;
use List::Util qw(sum min max shuffle);
binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my ($PIALIGN_DIR, $WORKING_DIR, $NO_EXPAND, $INPUT, $MERGE_UNARY, $LETRAC_DIR, $FORCE, $VERBOSE, $LAST_STEP, $INCLUDE_FAIL);
my ($VOID_SPAN, $BARE_RULE, $THREE_SYNC, $MAX_SIZE,$ALIGN,$MANUAL);
my $MAX_SIZE = "4";

GetOptions(
    # Necessary
    "letrac-dir=s" => \$LETRAC_DIR,
    "pialign-dir=s" => \$PIALIGN_DIR,
    "working-dir=s" => \$WORKING_DIR,
    "input-file=s" => \$INPUT,
    "last-step=s" => \$LAST_STEP,
    "three-sync"=> \$THREE_SYNC,
    "verbose!" => \$VERBOSE,
    "include-fail!" => \$INCLUDE_FAIL,
    "merge-unary!" => \$MERGE_UNARY,
	"void-span!" => \$VOID_SPAN,
	"bare-rule!" => \$BARE_RULE,
    "no-expand!" => \$NO_EXPAND,
    "max-size=s" => \$MAX_SIZE,
    "force!" => \$FORCE,
    "align=s" => \$ALIGN,
    "manual=s" => \$MANUAL,
);

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
safesystem("mkdir $WORKING_DIR/model");

# Preparing input for alignment
safesystem("$LETRAC_DIR/script/extract/input_preprocess.py < $INPUT > $WORKING_DIR/data/$file_name.preprocess");

# Creating input for alignment
safesystem("mkdir $WORKING_DIR/align");
my $manual = $MANUAL ? " --manual $MANUAL" : "";
safesystem("$LETRAC_DIR/script/extract/align-gen.py$manual --osent $WORKING_DIR/data/$file_name.sent --ologic $WORKING_DIR/data/$file_name.fol --input $WORKING_DIR/data/$file_name.preprocess") or die "Failed on creating input for alignment";
safesystem("$LETRAC_DIR/script/extract/swr.py < $WORKING_DIR/data/$file_name.sent > $WORKING_DIR/data/$file_name.kword") if ($THREE_SYNC);
exit(0) if $LAST_STEP eq "input";

# Running Alignment
if (not $ALIGN) {
    $ALIGN = "$WORKING_DIR/align/align.txt";
    safesystem("$PIALIGN_DIR/src/bin/pialign $WORKING_DIR/data/$file_name.sent.gin $WORKING_DIR/data/$file_name.fol.gin $WORKING_DIR/align/align-out. 2> $WORKING_DIR/align/pialign-log.txt") or die "Failed on running alignment";
    safesystem("$PIALIGN_DIR/script/itgstats.pl talign < $WORKING_DIR/align/align-out.1.samp > $ALIGN") or die "Failed on combining alignment";
} 

# Visualizing alignment
safesystem("$LETRAC_DIR/script/extract/cut-line.py $WORKING_DIR/data/$file_name.fol.gin $WORKING_DIR/data/$file_name.sent > $WORKING_DIR/data/$file_name.fol.visin");
safesystem("$LETRAC_DIR/script/extract/visualize.pl $WORKING_DIR/data/$file_name.sent $WORKING_DIR/data/$file_name.fol.visin $ALIGN 2 1 > $WORKING_DIR/align/align.vis");
exit(0) if $LAST_STEP eq "align"; 

# Make it isomorphic
safesystem("mkdir $WORKING_DIR/iso");
safesystem("$LETRAC_DIR/script/extract/make-isomorphic.py --sent $WORKING_DIR/data/$file_name.sent --fol $WORKING_DIR/data/$file_name.fol --align $ALIGN --input $WORKING_DIR/data/$file_name.preprocess --out $WORKING_DIR/iso/$file_name.ism");
exit(0) if $LAST_STEP eq "isomorph"; 

# lexical-acquisition
my $lex_command = "$LETRAC_DIR/script/extract/lexical-acq.py --out_num_rule $WORKING_DIR/data/$file_name.nextract --input $WORKING_DIR/iso/$file_name.ism --sent $WORKING_DIR/data/$file_name.sent --fol $WORKING_DIR/data/$file_name.fol --align $ALIGN --max_size $MAX_SIZE";
$lex_command .= " --verbose" if $VERBOSE;
$lex_command .= " --include_fail" if $INCLUDE_FAIL;
$lex_command .= " --merge_unary" if $MERGE_UNARY;
$lex_command .= " --void_span" if $VOID_SPAN;
$lex_command .= " --bare_rule" if $BARE_RULE;
$lex_command .= " --three_sync" if $THREE_SYNC;
$lex_command .= " --no_expand" if $NO_EXPAND;
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
