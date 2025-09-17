#! /bin/bash

#  参数1：proc_dir；该程序所在的文件夹
#  参数2：path；当前测序仪正在写入的fastq文件的文件夹路径
#  参数3: out_dir: 本次分析结果总文件夹

for i in `ls ${2}`
do
if [[ ${i} == *fastq ]]
then
${1}/softwares/seqtk-master/seqtk seq -A ${2}/${i} > ${1}${3}/final_out/reads_fasta/${i:0:`expr ${#i} - 5`}fasta
fi
done
 