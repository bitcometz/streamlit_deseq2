library(DESeq2)

# 从命令行获取参数
args <- commandArgs(trailingOnly = TRUE)

# 解析参数
exp_file   <- args[1]
meta_file  <- args[2]
outfile    <- args[3]

data       <- read.csv(exp_file, header = TRUE, row.names = 1)
group_info <- read.csv(meta_file)
group      <- factor(group_info$group)
dds        <- DESeqDataSetFromMatrix(countData = data, colData = data.frame(group), design = ~ group)

dds        <- DESeq(dds)
res        <- results(dds)

write.csv(res, file = outfile, row.names = TRUE)
