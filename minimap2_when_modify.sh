#! /bin/bash

#  ����1��proc_dir���ó������ڵ��ļ���
#  ����2��fullpath����ǰ����������д���fastq�ļ���ȫ·��
#  ����3��str(n_file)����ǰ����������д��ĵ�n_file���ļ�
#  ����4���趨���еĺ���
#  ����5: out_dir: ���η���������ļ���




comm -13 --nocheck-order ${1}${5}/intermediate/intermediate1_fastq/reads${3}_part.fastq ${2} > ${1}${5}/intermediate/intermediate2_newfastq/reads${3}_new.fastq
# ȡ�������reads��������[~/intermediate/intermediate/intermediate2_newfastq/]

cp ${2} ${1}${5}/intermediate/intermediate1_fastq/reads${3}_part.fastq
# ����������д���fastq�ļ����Ƶ���ʱ�ļ��У���������һ��fastq�ļ���

${1}/softwares/minimap2-2.26_x64-linux/minimap2 -t ${4} -a -x map-ont \
${1}/db/Vertebrata_Vgenome.mmi ${1}${5}/intermediate/intermediate2_newfastq/reads${3}_new.fastq | \
grep -v "^@" - | awk -F'\t' 'and($2, 0x4) == 0 { print }' > ${1}${5}/intermediate/intermediate3_minimap2/reads${3}_part.sam
# �ȶԣ���������intermediate3_minimap2�ļ���
# <-a : ��sam��ʽ������>	<-x map-ont : Ԥ��Ϊ���׿�������ο�������ıȶ�>

cat ${1}${5}/intermediate/intermediate3_minimap2/reads${3}_part.sam >> ${1}${5}/final_out/minimap2_out/reads${3}.sam
# �㼯�ȶԽ����[~/final_out/minimap2_out]�ļ���

