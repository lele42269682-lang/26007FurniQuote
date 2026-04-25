"""通用枚举与类型（跨模块共享）"""
from __future__ import annotations

from enum import Enum


class CustomerTier(str, Enum):
    """客户级别（5级，影响定价系数）"""
    L1 = "L1"   # 长期设计公司 + 零售经销商（×1.0 基准）
    L2 = "L2"   # 散单设计师（×1.2）
    L3 = "L3"   # 零售客户（×1.5~1.6）
    L4 = "L4"   # 大型工程酒店（≈L1）
    L5 = "L5"   # 美国批发商等（锁价）


class PriceAcceptance(str, Enum):
    """客户价格承受力（影响定价微调）"""
    A = "A"   # 不敏感（×1.1~1.2）
    B = "B"   # 正常（×1.0 默认）
    C = "C"   # 敏感（×0.9~0.95）


class RegionCode(str, Enum):
    """地区代码（影响地区消费力系数 + 客户编号生成）"""
    US = "US"   # 美国
    AU = "AU"   # 澳大利亚
    AE = "AE"   # 阿联酋（迪拜）
    SA = "SA"   # 沙特
    RU = "RU"   # 俄罗斯
    AM = "AM"   # 亚美尼亚
    ID = "ID"   # 印尼
    MY = "MY"   # 马来西亚
    TH = "TH"   # 泰国
    CN = "CN"   # 中国国内


class ProductCategory(str, Enum):
    """产品品类（用于产品编号前缀）"""
    SF = "SF"   # 沙发 Sofa
    BD = "BD"   # 床架 Bed
    CB = "CB"   # 橱柜 Cabinet
    TB = "TB"   # 餐桌 Table
    CH = "CH"   # 椅子 Chair
