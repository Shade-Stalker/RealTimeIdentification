#! /bin/bash

#  参数1：proc_dir；该程序所在的文件夹
#  参数2：fullpath；当前测序仪正在写入的fastq文件的全路径
#  参数3：str(n_file)；当前测序仪正在写入的第n_file个文件
#  参数4：设定运行的核数
#  参数5: out_dir: 本次分析结果总文件夹





cp ${2} ${1}${5}/intermediate/intermediate1_fastq/reads${3}_part.fastq
# 将新建的测序文件复制到临时文件夹

# $1"/softwares/seqtk-master/seqtk" seq -A $1$5"/intermediate/intermediate1_fastq/reads"$3"_part.fastq" > $1$5"/intermediate/intermediate2_fasta/reads"$3"_part.fasta"
# fastq格式转化为fasta格式 (弃，无用)

${1}/softwares/minimap2-2.26_x64-linux/minimap2 -t ${4} -a -x map-ont \
${1}/db/Vertebrata_Vgenome.mmi ${1}${5}/intermediate/intermediate1_fastq/reads${3}_part.fastq | \
grep -v "^@" - | awk -F'\t' 'and($2, 0x4) == 0 { print }' > ${1}${5}/intermediate/intermediate3_minimap2/reads${3}_part.sam
# 比对，结果输出至intermediate3_minimap2文件夹

cat ${1}${5}/intermediate/intermediate3_minimap2/reads${3}_part.sam >> ${1}${5}/final_out/minimap2_out/reads${3}.sam
# 汇集minimap2的比对结果结果到[~/final_out/minimap2_out/]文件夹