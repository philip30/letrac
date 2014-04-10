#!/usr/bin/perl

use strict;
use utf8;
use Getopt::Long;
use List::Util qw(sum min max shuffle);
binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my ($PIALIGN_DIR, $WORKING_DIR, $INPUT, $MERGE_UNARY, $LETRAC_DIR, $FORCE, $TRANSLATION_RULE, $VERBOSE, $LAST_STEP, $INCLUDE_FAIL);

GetOptions(
    # Necessary
    "letrac-dir=s" => \$LETRAC_DIR,
    "pialign-dir=s" => \$PIALIGN_DIR,
    "working-dir=s" => \$WORKING_DIR,
    "input-file=s" => \$INPUT,
    "translation-rule!" => \$TRANSLATION_RULE,
    "last-step=s" => \$LAST_STEP,
    "verbose!" => \$VERBOSE,
    "include-fail!" => \$INCLUDE_FAIL,
    "merge-unary!" => \$MERGE_UNARY,
    "force!" => \$FORCE
);

# Sanity check
if((not $PIALIGN_DIR) or (not $WORKING_DIR) or (not $INPUT) or (not $LETRAC_DIR)) {
    die "Must specify pialign-dir, working-dir, input, and letrac-dir\n";
}

if(@ARGV != 0) {
    print STDERR "Usage: $0 -pialign-dir /path/to/pialign -working-dir WORKING_DIR -input INPUT_FILE -letrac-dir LETRAC_DIR\n";
    exit 1;
}

### START HERE
my $file_name = substr($INPUT, rindex($INPUT, '/')+1);

# CREATING DIR
if (not (mkdir $WORKING_DIR) and $FORCE) {
    safesystem("rm -rf $WORKING_DIR");
    safesystem("mkdir $WORKING_DIR");
} elsif (not $FORCE) {
    die "couldn't mkdir $WORKING_DIR";
}
safesystem("mkdir $WORKING_DIR/data");
safesystem("mkdir $WORKING_DIR/model");

# Creating input for alignment
safesystem("mkdir $WORKING_DIR/align");
safesystem("$LETRAC_DIR/script/align-gen.py --osent $WORKING_DIR/data/$file_name.sent --ologic $WORKING_DIR/data/$file_name.fol --input $INPUT") or die "Failed on creating input for alignment";
exit(0) if $LAST_STEP eq "input";

# Running Alignment
safesystem("$PIALIGN_DIR/src/bin/pialign $WORKING_DIR/data/$file_name.sent.gin $WORKING_DIR/data/$file_name.fol.gin $WORKING_DIR/align/align-out. 2> $WORKING_DIR/align/pialign-log.txt") or die "Failed on running alignment";
safesystem("$PIALIGN_DIR/script/itgstats.pl talign < $WORKING_DIR/align/align-out.1.samp > $WORKING_DIR/align/align.txt") or die "Failed on combining alignment";

# Visualizing alignment
safesystem("$LETRAC_DIR/script/cut-line.py $WORKING_DIR/data/$file_name.fol.gin $WORKING_DIR/data/$file_name.sent > $WORKING_DIR/data/$file_name.fol.visin");
safesystem("$LETRAC_DIR/script/visualize.pl $WORKING_DIR/data/$file_name.sent $WORKING_DIR/data/$file_name.fol.visin $WORKING_DIR/align/align.txt 2 1 > $WORKING_DIR/align/tal-vis.txt");
exit(0) if $LAST_STEP eq "align"; 

# Make it isomorphic
safesystem("mkdir $WORKING_DIR/iso");
safesystem("$LETRAC_DIR/script/make-isomorphic.py --sent $WORKING_DIR/data/$file_name.sent --fol $WORKING_DIR/data/$file_name.fol --align $WORKING_DIR/align/align.txt --input $INPUT --out $WORKING_DIR/iso/$file_name.ism");
exit(0) if $LAST_STEP eq "isomorph"; 

# lexical-acquisition
my $lex_command = "$LETRAC_DIR/script/lexical-acq.py --input $WORKING_DIR/iso/$file_name.ism --sent $WORKING_DIR/data/$file_name.sent --fol $WORKING_DIR/data/$file_name.fol --align $WORKING_DIR/align/align.txt";
$lex_command .= " --verbose" if $VERBOSE;
$lex_command .= " --translation_rule" if $TRANSLATION_RULE;
$lex_command .= " --include_fail" if $INCLUDE_FAIL;
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
