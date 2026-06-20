#
# @Author  : zhuy
# @Date    : 2026/1/10 17:32
# @Desc    : 预设的tsv文件过滤器
#

# --- 定义灵活的过滤器工厂 (使用列名) ---

def column_not_nan(col_name):
    """排除指定列中值为 NaN 的行 (只保留有值的行)"""
    return lambda df: df[col_name].notna()

def column_gt(col_name, value):
    """数值大于某值"""
    return lambda df: df[col_name] > value

def column_contains(col_name, keyword):
    """字符串包含某关键字"""
    return lambda df: df[col_name].str.contains(keyword, na=False)

def column_not_contains(col_name, keyword):
    """字符串不包含某关键字"""
    return lambda df: ~df[col_name].str.contains(keyword, na=False)

def column_in(col_name, options_list):
    """值在某个列表内"""
    return lambda df: df[col_name].isin(options_list)

def select_columns(columns):
    """只保留指定的列"""
    return lambda df: df[columns]

def drop_columns(columns):
    """排除指定的列"""
    return lambda df: df.drop(columns=columns, errors='ignore')

def regex_match(col_name, pattern):
    """使用正则表达式进行高级匹配"""
    return lambda df: df[col_name].str.contains(pattern, regex=True, na=False)

def fast_assign(**kwargs):
    """
    利用 Pandas assign 一次性增加多个动态列
    用法: fast_assign(Total=lambda x: x.a + x.b, Tax=lambda x: x.Total * 0.1)
    """
    return lambda df: df.assign(**kwargs)