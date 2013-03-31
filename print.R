setwd("~/repos/work_analysis/")
files<-list.files(pattern=".dat")
for (f in files)
{
  currenttable <- read.table(f, header=T, quote="\"")
  hist(currenttable$max, breaks=50, main=f)
  print (sprintf("%s min:%.0f max:%.0f", f, mean(currenttable$min), mean(currenttable$max)))
}