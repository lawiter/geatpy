"""
i_awGA_tmplet.py - 基于交互式适应性权重聚合法(i-awGA)求解多目标优化问题的编程模板

算法描述：
    本模板实现了基于改进的交互式适应性权重聚合法(i-awGA)的多目标优化搜索，
    改进之处是将原i-awGA中使用的Deb非支配排序法变为快速非支配排序法，
    并维护一个全局帕累托最优集来实现帕累托前沿的搜索，故并不需要保证种群所有个体都是非支配的
    
"""
import numpy as np
import geatpy as ga # 导入geatpy库
import time

def i_awGA(AIM_M, AIM_F, NIND, ranges, borders, precisions, MAXGEN, SUBPOP, GGAP, selectStyle, recombinStyle, recopt, pm, maxormin):
    """==========================初始化配置==========================="""
    # 获取目标函数和罚函数
    aimfuc = getattr(AIM_M, AIM_F) # 获得目标函数
    FieldDR = ga.crtfld(ranges, borders, precisions)
    """=========================开始遗传算法进化======================="""
    Chrom = ga.crtrp(NIND, FieldDR) # 创建简单离散种群
    ObjV = aimfuc(Chrom) # 计算种群目标函数值
    NDSet = np.zeros((0, ObjV.shape[1])) # 定义帕累托最优解集合(初始为空集)
    start_time = time.time() # 开始计时
    # 开始进化！！
    for gen in range(MAXGEN):
        if NDSet.shape[0] > 2 * ObjV.shape[0]:
            break
        [CombinObjV, weight] = ga.awGA(ObjV) # 适应性权重法求聚合目标函数值
        FitnV  = ga.ranking(maxormin * CombinObjV) # 根据加权单目标计算适应度
        [FitnV, frontIdx] = ga.ndominfast(maxormin * ObjV, FitnV) # 求种群的非支配个体，并更新适应度
        
        # 更新帕累托最优集以及种群非支配个体的适应度
        [FitnV, NDSet, repnum] = ga.upNDSet(FitnV, maxormin * ObjV, maxormin * NDSet, frontIdx)
        
        # 进行遗传操作！！
        SelCh=ga.selecting(selectStyle, Chrom, FitnV, GGAP, SUBPOP) # 选择
        SelCh=ga.recombin(recombinStyle, SelCh, recopt, SUBPOP) #交叉
        SelCh=ga.mutbga(SelCh, FieldDR, pm) # 变异
        if repnum > Chrom.shape[0] * 0.1: # 进行一次高斯变异
            SelCh=ga.mutgau(SelCh, FieldDR, pm) # 高斯变异
        ObjVSel = aimfuc(SelCh) # 求育种个体的目标函数值
        [CombinObjV, weight] = ga.awGA(maxormin * ObjVSel) # 适应性权重法求聚合目标函数值
        FitnVSel = ga.ranking(maxormin * CombinObjV) # 根据聚合目标求育种个体适应度
        [Chrom,ObjV] = ga.reins(Chrom,SelCh,SUBPOP,1,0.9,FitnV,FitnVSel,ObjV,ObjVSel) #重插入
        
    end_time = time.time() # 结束计时    
    # 返回帕累托最优集以及执行时间
    return [ObjV, NDSet, end_time - start_time]