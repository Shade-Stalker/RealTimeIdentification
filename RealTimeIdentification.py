# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 10:46:31 2023

尚未完成：
1.读取手动输入路径
2.任务列表的显示与功能设置
3.线程的更细节的设置,解决卡顿问题
4.每次只有新文件创建时，显示表格才更新————需解决

需立即解决： 双击路径问题，函数 OpenResultDir

@author: LiFengyi
"""

import os, signal, datetime, sys, csv
proc_dir = os.path.split(os.path.realpath(__file__))[0] # 当前脚本代码所在文件夹,末尾未加"/"
# sys.path.append(proc_dir + "/pypackages")

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import scrolledtext

import threading

# import inotify
import inotify.adapters
import pandas as pd

import multiprocessing


######
### 窗口设计
######

root_UI = tk.Tk()
# 创建底层窗口
root_UI.title("RealTimeIdentification")
root_UI.geometry("1200x800+100+100")
# 设定窗口初始大小和位置

frame1_menu = ttk.Frame(root_UI, style = "1.TFrame", relief = "sunken")
frame1_menu.pack(fill = "x", anchor = "n")
# 创建顶部框架1

button1_start = ttk.Button(frame1_menu, text = "开始")
button1_start.pack(side = "left")
# 在顶部框架中放置开始按钮

entry1_path = ttk.Entry(frame1_menu)
entry1_path.pack(side = "left", fill = "x", expand = 1)
# 在顶部框架中放置待测文件夹路径栏

photo1_OpenFile = tk.PhotoImage(file = proc_dir + "/openfile.gif")
button2_OpenFile = ttk.Button(frame1_menu, image = photo1_OpenFile)
button2_OpenFile.pack(side = "right")
# 在顶部框架中放置选择文件夹路径的按钮

separator = ttk.Separator(root_UI)
separator.pack(padx=2, fill='x')
# 创建分割线，(padx: 分割线离左右两边界的距离)

pw1 = tk.PanedWindow(root_UI, orient = "horizontal", sashrelief = "sunken")
pw1.pack(fill = "both", expand = 1)
# 创建第一个大小可调节的面板，作为主面板，方向为水平

pw1_left = tk.PanedWindow(orient = "vertical", sashrelief = "sunken")
pw1.add(pw1_left)
# 创建第二个大小可调节的面板，方向为竖直，并添加至第一个面板中作为子面板，置于左边

frame2_ResultDetails = ttk.Frame(pw1, relief = "sunken")
pw1.add(frame2_ResultDetails)
# 在第一个面板中添加框架2，置于右边，用于放置输出结果表格

frame3_status = ttk.Frame(pw1_left, relief = "sunken", \
                          width = 300, \
                          height = 300
)
pw1_left.add(frame3_status)
# 在子面板中添加框架3，置于子面板内上方，用于放置状态栏

frame4_ResultList = ttk.Frame(pw1_left, relief = "sunken")
pw1_left.add(frame4_ResultList)
# 在子面板中添加框架4，置于子面板内下方，用于放置多次检测结果的列表

label1_status = ttk.Label(frame3_status, text = "运行状态", relief = "flat")
label1_status.pack(pady = 2, anchor = "nw")
# 创建状态栏标签，置于框架3顶端

text1_status = scrolledtext.ScrolledText(frame3_status, \
                                            width = 40)
text1_status.pack(fill = "both", expand = 1)
# 创建文本框，置于框架3中，用于显示程序运行状态

label2_ResultList = ttk.Label(frame4_ResultList, text = "任务列表")
label2_ResultList.pack(pady = 2, anchor = "nw")
# 创建结果列表标签，置于框架4顶端

scrollbar_ResultList = ttk.Scrollbar(frame4_ResultList)
listbox1_ResultList = tk.Listbox(frame4_ResultList, yscrollcommand = scrollbar_ResultList.set)
scrollbar_ResultList.config(command = listbox1_ResultList.yview)
listbox1_ResultList.pack(side = "left", fill = "both", expand = 1)
scrollbar_ResultList.pack(side = "right", fill = "y", expand = 0)
# 创建列表框，用于显示多次结果文件的列表

label3_ResultDetails = ttk.Label(frame2_ResultDetails, text = "鉴定结果")
label3_ResultDetails.pack(pady = 2, anchor = "nw")
# 创建详细结果的标签，置于框架2顶端

treeview1_ResultDetails = ttk.Treeview(frame2_ResultDetails)
treeview1_ResultDetails.config(column = ["reads数目", "病毒名", "病毒参考ID", "宿主名", "宿主参考ID", "链接"])
treeview1_ResultDetails.heading("#0", text = "序号"), treeview1_ResultDetails.heading("reads数目", text = "reads数目")
treeview1_ResultDetails.heading("病毒名", text = "病毒名"), treeview1_ResultDetails.heading("病毒参考ID", text = "病毒参考ID")
treeview1_ResultDetails.heading("宿主名", text = "宿主名"), treeview1_ResultDetails.heading("宿主参考ID", text = "宿主参考ID")
treeview1_ResultDetails.heading("链接", text = "链接")
treeview1_ResultDetails.column("#0", width = 50, stretch = 0), treeview1_ResultDetails.column("reads数目", width = 80, stretch = 0)
treeview1_ResultDetails.column("病毒参考ID", width = 90), treeview1_ResultDetails.column("宿主参考ID", width = 70)
treeview1_ResultDetails.pack(fill = "both", expand = 1)
# 创建表格，用于显示最终鉴定结果

######
### 函数嵌入
######

### 获取测序输出文件夹路径

SeqDic_pathTK = tk.StringVar()
# 设置可变字符串用于显示路径

def get_path():
    """ 
    点击按钮时，获取按钮选定的文件夹路径
    """
    global SeqDic_path
    dir_path = filedialog.askdirectory()
    SeqDic_path = dir_path
    SeqDic_pathTK.set(dir_path)
    # 函数终点

entry1_path.config(textvariable = SeqDic_pathTK)
# 显示选择的路径
button2_OpenFile.config(command = get_path)
# 点击文件夹按钮，选择路径


def thread_it(func, *args):
    """
    函数多线程运行
    func:待运行的函数
    args:?
    
    """
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()
    # 函数终点

    
def SearchDetails(query_row, db):
    """
    从元数据中提取输入的基因组ID所在的行
    query_row : target_IDs的行，包含鉴定出的ID，列名"sseqid"
    db : 病毒数据库元数据
    """
    query_position = db["refseq id"].str.contains(query_row["sseqid"][0:-2])
    query_details = db.loc[query_position, : ].reset_index(drop = True)
    query_details.insert(0, "count", query_row["count"])
    query_details.insert(0, "sseqid", query_row["sseqid"])
    return query_details
    # 函数终点

def AddNewResults(NewDf_SubDf):
    """
    将新的检测结果整合到总结果表格中
    当已存在相同结果时，累加reads数
    当结果为全新时，添加至表格后
    ----------
    NewDf_SubDf : 新结果中的每一行，其类型为表格
    """
    global IdentifiedViruses_final
    if any(IdentifiedViruses_final["sseqid"].values == NewDf_SubDf.loc[0 ,"sseqid"]):
        IdentifiedViruses_final.loc[IdentifiedViruses_final["sseqid"].values == NewDf_SubDf.loc[0, "sseqid"], "count"] += NewDf_SubDf.loc[0, "count"]
    else:
        IdentifiedViruses_final = pd.concat([IdentifiedViruses_final, NewDf_SubDf])
    # 函数终点
    

def getFlist(path):
    """
    获取path文件夹下的所有文件（不包括子文件夹）
    path:文件夹路径
    return:文件名list
    """
    for root, dirs, files in os.walk(path):
        print('root_dir:', root)  #当前路径
        print('sub_dirs:', dirs)   #子文件夹
        print('files:', files)     #文件名称，返回list类型
        return files # 第一次循环就终止，返回最外层文件
    # 函数终点

def getDirList(path):
    """
    获取path文件夹下的所有初级子文件夹
    path:文件夹路径
    return:文件名list
    """
    for root, dirs, files in os.walk(path):
        print('root_dir:', root)  #当前路径file
        print('sub_dirs:', dirs)   #子文件夹
        print('files:', files)     #文件名称，返回list类型
        dirs.sort()
        return dirs


def ShowResultTable(pointless = None):
    """
    点击历史结果时，显示检测结果列表

    """
    try:
        treeview1_ResultDetails.delete(*treeview1_ResultDetails.get_children())
        results_tbl = pd.read_csv(proc_dir + \
                                  "/output/" + \
                                  listbox1_ResultList.get(listbox1_ResultList.curselection()) + \
                                  "/final_out/Identified_Viruses.tsv", sep = '\t')
            
        results_tbl["count"] = results_tbl["count"].apply(lambda x : "" if pd.isnull(x) else x)
        results_tbl["count"] = results_tbl["count"].apply(lambda x : str(x)[0 : len(str(x))-2])
        results_tbl["host tax id"] = results_tbl["host tax id"].astype("int")
        
        for i in results_tbl.index:
            treeview1_ResultDetails.insert("", i, text = results_tbl.loc[i, "Unnamed: 0"], \
                                           values = list(results_tbl.loc[i, ["count", "virus name", "sseqid", "host name", "host tax id"]]))
    except:
        CantOpen_message = tk.messagebox.showerror("错误", "结果文件不存在或不完整")
        ######## tk.messagebox.showerror("错误", "结果文件不存在或不完整")
    # 函数终点
    
def OpenResultDir(pointless = None):
    """
    双击历史结果时，打开结果文件夹，linux系统

    """
    #os.system("explorer " + (proc_dir + "/output/").replace("/", "\\") + \
    #         listbox1_ResultList.get(listbox1_ResultList.curselection()))
    # windows系统↑
    
#    try:
#        os.system("open " + (proc_dir + "/output/") + listbox1_ResultList.get(listbox1_ResultList.curselection()))
#        print(listbox1_ResultList.get(listbox1_ResultList.curselection()))
#    except:
    os.system("nautilus " + (proc_dir + "/output/") + listbox1_ResultList.get(listbox1_ResultList.curselection()))
    print(listbox1_ResultList.get(listbox1_ResultList.curselection()))
    
def RealTimeIdentification (infiledir):
    """
    主函数，进行测序监测、比对、结果分析、结果显示、序列提取一系列操作
    """
    
    
    global IdentifiedViruses_final
    global minimap2_cols
    # 
    
    date_today = str(datetime.date.today())
    out_dir = "/output/" + date_today + "_" + infiledir.split("/")[-1]
    
    os.mkdir(proc_dir + out_dir)
    os.mkdir(proc_dir + out_dir + "/intermediate")
    os.mkdir(proc_dir + out_dir + "/intermediate/intermediate1_fastq")
    os.mkdir(proc_dir + out_dir + "/intermediate/intermediate2_newfastq")
    os.mkdir(proc_dir + out_dir + "/intermediate/intermediate3_minimap2")
    os.mkdir(proc_dir + out_dir + "/final_out")
    os.mkdir(proc_dir + out_dir + "/final_out/minimap2_out")
    os.mkdir(proc_dir + out_dir + "/final_out/reads_fasta")
    os.mkdir(proc_dir + out_dir + "/final_out/IdentifiedViruses_Reads")
    # 创建分析结果文件夹集
    
    # print("创建分析结果文件夹")
    text1_status.insert("end", "创建分析结果文件夹\n")
    text1_status.update()
    # 状态栏输出
    
    listbox1_ResultList.insert("end", date_today + "_" + infiledir.split("/")[-1])
    # 左下角历史结果列表中添加本次结果
    
    metadata_db = pd.read_csv(proc_dir + "/metadata_db.tsv", sep = "\t")
    # 读取病毒数据库的元数据
    
    IdentifiedViruses_final = pd.DataFrame(columns = ["sseqid", "count", "virus tax id", "virus name", \
                                              "virus lineage", "refseq id", "KEGG GENOME", \
                                              "KEGG DISEASE", "DISEASE", "host tax id", \
                                              "host name", "host lineage", "pmid", "evidence", \
                                              "sample type", "source organism"])
    # 最终表格及其表头设定
    
    minimap2_cols = ["qseqid", "flag", "sseqid", "pos", "mapq", "cigar"]
    # sam结果表格的抬头

    
    ###### 测序过程中进行比对鉴定，统计结果输出
    
    #notifier = inotify.adapters.Inotify()
    #notifier.add_watch(infiledir)
    #  配置文件修改监视器
    notifier = inotify.adapters.InotifyTree(infiledir)
    # 正式版中使用，可监视次级文件夹
    
    class TimeoutException(Exception):
        pass
    def timeout_handler(signum, frame):
        raise TimeoutException
    signal.signal(signal.SIGALRM, timeout_handler)
    #  配置超时监测
    
    n_file = 10000
    #  测序文件计数初始值
    
    ### 开始监测和鉴定
    # print("开始监测，等待测序开始......")
    text1_status.insert("end", "开始监测，等待测序开始......\n")
    text1_status.update()
    text1_status.see("end")
    
    # probe_n = 0
    # 调试用
    
    try:
        for event in notifier.event_gen(yield_nones = False): # yield_nones=True：无事发生时定时输出None
            signal.alarm(0)
            # 重置定时器
    
            # 调试用
            # print(event)
            
            (_, type_names, path, filename) = event
            
            if path.endswith("ResultFiles/fastq"):
                # 定位正确输出文件夹，后续代码注意缩进。
    
                # print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(path, filename, type_names))
                # print("probe = " + str(probe_n))
                # 用于测试，记录循环状态。
                
                fq_path = path
                
                if filename.endswith("fastq"):
                    if type_names == ['IN_CREATE'] or type_names == ['IN_MODIFY']:
                        fullpath = path + "/" + filename
                        # 测序结果文件全路径
                        
                        if type_names == ['IN_CREATE']:
                        # 每次新测序结果文件创建时
                            n_file += 1
                            # 结果文件计数
                            nfile_str = str(n_file)[1:len(str(n_file))]
                            
                            print("第{}个测序文件生成，处理中......".format(nfile_str))
                            text1_status.insert("end", "第{}个测序文件生成，处理中......\n".format(nfile_str))
                            print("文件路径：{}".format(fullpath))
                            text1_status.insert("end", "文件路径：{}\n".format(fullpath))
                            text1_status.update()
                            text1_status.see("end")
                            
                            sh_1 = "sh " + proc_dir + "/minimap2_when_create.sh " + \
                                proc_dir + " " + \
                                fullpath + " " + \
                                nfile_str + " " + \
                                "7" + " " + \
                                out_dir
                            os.popen(sh_1).read()
                            # 使用shell命令将结果文件复制到中间文件夹，若同时有reads输入，进行比对。
        
                        elif type_names == ['IN_MODIFY']:
                        # 每次新测序结果输出到结果文件时
                            if n_file == 10000: # when start identifying in the middle of sequencing
                                n_file += 1
                                # 结果文件计数
                                nfile_str = str(n_file)[1:len(str(n_file))]
                            
                                print("第{}个测序文件生成，处理中......".format(nfile_str))
                                text1_status.insert("end", "第{}个测序文件生成，处理中......\n".format(nfile_str))
                                print("文件路径：{}".format(fullpath))
                                text1_status.insert("end", "文件路径：{}\n".format(fullpath))
                                text1_status.update()
                                text1_status.see("end")
                            
                                sh_1 = "sh " + proc_dir + "/minimap2_when_create.sh " + \
                                    proc_dir + " " + \
                                    fullpath + " " + \
                                    nfile_str + " " + \
                                    "7" + " " + \
                                    out_dir
                                os.popen(sh_1).read()
                                # 使用shell命令将结果文件复制到中间文件夹，若同时有reads输入，进行比对。
                            else:
                                sh_2 = "sh " + proc_dir + "/minimap2_when_modify.sh " + \
                                    proc_dir + " " + \
                                    fullpath + " " + \
                                    nfile_str + " " + \
                                    "7" + " " + \
                                    out_dir
                                os.popen(sh_2).read()
                            # 将新增结果复制到中间文件夹，并进行比对.
                        
                        ######
                        #统计结果处理
                        ######
                        
                        minimap2_output = pd.read_csv(proc_dir + out_dir + "/intermediate/intermediate3_minimap2/reads" + \
                                                   nfile_str + "_part.sam", \
                                                   sep = "\t", usecols = [x for x in range(0,6)], \
                                                   names = minimap2_cols, \
                                                   quoting = csv.QUOTE_NONE
                                                   )
                        # 读取的比对结果
                        
                        if not minimap2_output.empty:
                            # 本次比对结果不为空时
                            
                            minimap2_output = minimap2_output.drop_duplicates(["qseqid", "sseqid"])
                            # 去除可能存在的同一reads和参考基因组的多段比对结果，保留一个。
                            
                            target_IDs = minimap2_output.value_counts(["sseqid"]).reset_index()
                            target_IDs.columns = ["sseqid","count"]
                            # 计算比对上每个参考基因组ID的reads数目，输出至target_IDs，并按数目大小排序                    
    
                            ###  提取鉴定的参考基因组所对应的病毒信息
                            
                            # metadata_dbX = metadata_db.loc[metadata_db["refseq id"].str.contains("|".join(target_IDs["sseqid"].apply(lambda x : x[0:-2]))),:]
                            # 需测试一下提前缩小表格更快，还是直接用总meta表格更快
                            identified_viruses = target_IDs.apply(lambda x : SearchDetails(x, metadata_db), axis = 1)
                            # 对target_IDs每行进行相同的函数操作，提取各ID所在的元数据行，输出于identified_viruses中。
                            
                            identified_viruses.apply(lambda x : AddNewResults(x))
                            # 将当前检测结果添加至总结果中
                            
    
                            IdentifiedViruses_final = IdentifiedViruses_final.sort_values(["count", "sseqid"], ascending = False)
                            # 再次按照reads数目排序
                            
                            ###  结果输出至UI界面
                            
                            IdentifiedViruses_show = IdentifiedViruses_final[:].copy()
                            
                            IdentifiedVirusesShow_NewIndex = []
                            IdentifiedVirusesShow_NewIndex_n = 0
                            for n_index in IdentifiedViruses_show.index:
                                if n_index == 0:
                                    IdentifiedVirusesShow_NewIndex_n += 1
                                else:
                                    IdentifiedViruses_show.loc[n_index, "count"] = ""
                                IdentifiedVirusesShow_NewIndex.append(IdentifiedVirusesShow_NewIndex_n)
                            IdentifiedViruses_show["newindex"] = IdentifiedVirusesShow_NewIndex
                            IdentifiedViruses_show = IdentifiedViruses_show.reset_index(drop = True)
                            # 为IdentifiedViruses_show重新设置索引（序号），相同的序列ID和病毒名的组合分配相同的序号。
                            # 存在相同的序列ID和病毒名的组合的原因：同一病毒具有多个不同宿主，数据库中以多行记录。
                            
                            IdentifiedViruses_show = IdentifiedViruses_show[["newindex", "count", "virus name", "sseqid", "host name", "host tax id"]]
                            # 提取要显示在UI中的列
                            
                            # IdentifiedViruses_show["count"] = IdentifiedViruses_show["count"].apply(lambda x : str(x)[0 : -2])
                            IdentifiedViruses_show["host tax id"] = IdentifiedViruses_show["host tax id"].astype("int")
                            # 将reads数目列和宿主tax ID列的数据格式由float修改为str（reads数目列有空白）和int，不显示小数点
                            
                            
                            
                            for row in treeview1_ResultDetails.get_children():
                                treeview1_ResultDetails.delete(row)
                            # 删除上一个显示的表格
                            for i in IdentifiedViruses_show.index:
                                treeview1_ResultDetails.insert("", i, text = IdentifiedViruses_show.loc[i, "newindex"], \
                                                               values = list(IdentifiedViruses_show.loc[i, ["count", "virus name", "sseqid", "host name", "host tax id"]]))
                            # 显示本次处理完的表格
                            text1_status.update() # 显示表格更新的暂时解决方案
                            text1_status.see("end") # 显示表格更新的暂时解决方案
  


                        
                    

    
            signal.alarm(1000)
            # 进程到达1000秒后，输出信号
    except TimeoutException:
        print("测序结束，开始后续分析")
        text1_status.insert("end", "测序结束，开始后续分析\n")
        text1_status.update()
        text1_status.see("end")
        
    ###### 测序结束，开始后续分析
    
    ###  预处理
    
    IdentifiedVirusesFinal_NewIndex = []
    IdentifiedVirusesFinal_NewIndex_n = 0
    for n_index in IdentifiedViruses_final.index:
        if n_index == 0:
            IdentifiedVirusesFinal_NewIndex_n += 1
        else:
            IdentifiedViruses_final.loc[n_index, "count"] = ""
        IdentifiedVirusesFinal_NewIndex.append(IdentifiedVirusesFinal_NewIndex_n)
    IdentifiedViruses_final.index = IdentifiedVirusesFinal_NewIndex
    # 为IdentifiedViruses_final重新设置索引（序号），相同的序列ID和病毒名的组合分配相同的序号。
    # 存在相同的序列ID和病毒名的组合的原因：同一病毒具有多个不同宿主，数据库中以多行记录。
    # 与IdentifiedViruses_show的处理类似
    
    IdentifiedViruses_final.to_csv(proc_dir + out_dir + "/final_out/Identified_Viruses.tsv", sep = "\t")
    print("输出鉴定结果总结表格")
    # 输出至文件Identified_Viruses.csv
    
    merge_sam = \
        "cat " + proc_dir + out_dir + "/final_out/minimap2_out/* > " + \
        proc_dir + out_dir + "/final_out/minimap2_out/all.sam"
    os.popen(merge_sam).read()
    # 合并所有比对结果,结果输出于minimap2_out文件夹
    
    minimap2_output = pd.read_csv(proc_dir + out_dir + "/final_out/minimap2_out/all.sam", sep = '\t', \
                                    usecols = [x for x in range(0,6)], names = minimap2_cols, quoting = csv.QUOTE_NONE)
    minimap2_output = minimap2_output.drop_duplicates(["qseqid", "sseqid"])
    # 读取合并的比对结果，并去除可能存在的同一reads和参考基因组的多段比对结果，保留一个。
    
    minimap2_output = minimap2_output.sort_values("sseqid")
    # minimap2_output["srank"] = minimap2_output["sseqid"].rank(method = "max")
    # 将比对结果按照参考基因组ID排序。# 并排名。
    
    print("proc_dir : " + proc_dir)
    print("path : " + path)
    print("out_dir" + out_dir)
    # test_20240311
    
    sh_3 = "bash " + proc_dir + "/conver_reads.sh " + \
                    proc_dir + " " + \
                    fq_path + " " + \
                    out_dir
    os.popen(sh_3).read()
    print("done") # test_20240311
    # reads 转化为fasta格式，结果输出于reads_fasta文件夹
    
    ###### 从原始测序数据中提取各已鉴定病毒的reads到各自的fasta文件
    
    ### 依据基因组ID从比对结果中提取fasta序列的抬头
    
    IdentifiedViruses_names = IdentifiedViruses_final[["sseqid", "virus name","count"]].drop_duplicates(["sseqid", "virus name"])
    IdentifiedViruses_names.index = IdentifiedViruses_names["virus name"]
    # 提取"sseqid""virus name""count"三列并以"sseqid"""virus name"两列去重，便于后续使用。
    # 一个virus name可能对应多个sseqid
    
    IdentifiedViruses_ReadsHead = pd.DataFrame(columns = IdentifiedViruses_final["virus name"].drop_duplicates())
    # 创建记录序列抬头的空表格
    IdentifiedViruses_count = pd.DataFrame(columns = ["virus name", "count"])
    # 创建记录各病毒reads数的空表格
    
    for n_VirusName in IdentifiedViruses_final["virus name"].drop_duplicates():
        nVirusID_position = IdentifiedViruses_names["virus name"].values == n_VirusName
        nVirus_ID = IdentifiedViruses_names.loc[nVirusID_position, "sseqid"]
        nVirus_reads = nVirus_ID.apply(lambda x : minimap2_output.loc[minimap2_output["sseqid"].values == x,\
                                                                  ["sseqid", "qseqid"]])
        nVirus_reads = pd.concat(nVirus_reads.values, axis = 0)
        IdentifiedViruses_ReadsHead[n_VirusName] = nVirus_reads["qseqid"].reset_index(drop = True)
        # 按照同一病毒对应的参考序列ID，从比对结果中提取比对上的reads抬头，并输入到记录表格的对应列。（同一病毒可能有多个参考序列）
        
        nVirus_count = int(IdentifiedViruses_names.loc[nVirusID_position, "count"].sum())
        nVirus_count = pd.DataFrame([n_VirusName, nVirus_count], index = ["virus name", "count"]).T
        IdentifiedViruses_count = pd.concat([IdentifiedViruses_count, nVirus_count])
        # 统计每一病毒的reads数目，并按行输入到记录表格。（同一病毒可能有多个参考序列）
    
    IdentifiedViruses_count.index = IdentifiedViruses_count["virus name"]
    # 以"virus name"列作为索引，便于后续文件命名时使用。
    
    n_file = 10000
    for n_Fafile in getFlist(proc_dir + out_dir + "/final_out/reads_fasta"):
        # 将各个序列文件分开操作，确保内存不溢出
        n_file += 1
        nfile_str = str(n_file)[1:len(str(n_file))]
        print("正在提取第{}个测序文件的病毒序列".format(nfile_str))
        text1_status.insert("end", "正在提取第{}个测序文件的病毒序列\n".format(nfile_str))
        text1_status.update()
        text1_status.see("end")
        # 更新状态栏
        
        reads_str = {}
        with open(proc_dir + out_dir + "/final_out/reads_fasta/" + n_Fafile, "r") as readsstr:
            for n_FaLines in readsstr.readlines():
                if n_FaLines.startswith(">"):
                    nread_head = n_FaLines.strip()
                    reads_str[nread_head] = []
                else:
                    reads_str[nread_head].append(n_FaLines.strip())
        reads_str = pd.DataFrame(reads_str).T.reset_index()
        reads_str.columns = ["head", "string"]
        # 将reads的fasta文件读取为字典，再转化为pd的数据框，减少程序运行时间。
        
        for n_VirusName1 in IdentifiedViruses_ReadsHead.columns:
            nReads_String = IdentifiedViruses_ReadsHead[n_VirusName1].dropna().apply(lambda x :\
                                                                              reads_str.loc[reads_str["head"].str.contains(x), : ])
            nReads_String = pd.concat(nReads_String.values, axis = 0)
            with open(proc_dir + out_dir + "/final_out/IdentifiedViruses_Reads/" + \
                      str(IdentifiedViruses_count.loc[n_VirusName1, "count"]) + "_" + n_VirusName1 + ".fasta", "a") as nReadsString:
                nReads_String.apply(lambda x : nReadsString.write(x["head"] + "\n" + x["string"] + "\n"), axis = 1)
            #  将当前fasta文件中属于当前病毒（n_VirusName1）的序列累加输出到对应名字的fasta文件
    print("运行结束")
    text1_status.insert("end", "运行结束\n")
    text1_status.update()
    text1_status.see("end")
    # 主函数终点

def process_it():
    """
    函数多进程运行
    func:待运行的函数
    args:?
    
    """
    p = multiprocessing.Process(target=RealTimeIdentification(SeqDic_path))
    p.start()

button1_start.config(command = process_it)
# 设置：点击开始按钮，运行主程序（函数），并以多线程的方式运行。

result_list = getDirList(proc_dir + "/output")

for result_n in result_list:
    listbox1_ResultList.insert("end", result_n)

listbox1_ResultList.bind('<Double-Button-1>', OpenResultDir)
listbox1_ResultList.bind('<ButtonRelease-1>', ShowResultTable)

root_UI.mainloop()
# 显示主窗口
