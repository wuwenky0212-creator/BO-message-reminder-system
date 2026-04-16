#!/usr/bin/env python3
"""
任务 1.2.4 验证脚本 (Python版本)
描述: 使用Python执行所有验证测试，提供跨平台支持
使用方法: python database/tests/validate_task_1_2_4.py
"""

import os
import sys
import subprocess
from typing import Tuple, Optional

# ANSI颜色代码
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

# 数据库配置（从环境变量读取，或使用默认值）
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'postgres'),
    'name': os.getenv('DB_NAME', 'message_reminder_db'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
}

def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)

def print_success(message: str):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")

def print_error(message: str):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {message}{Colors.NC}")

def print_warning(message: str):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.NC}")

def print_info(message: str):
    """打印信息消息"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.NC}")

def run_psql_command(sql: str, quiet: bool = False) -> Tuple[bool, str]:
    """
    执行psql命令
    
    Args:
        sql: SQL命令
        quiet: 是否静默模式（不显示输出）
    
    Returns:
        (成功标志, 输出内容)
    """
    cmd = [
        'psql',
        '-U', DB_CONFIG['user'],
        '-h', DB_CONFIG['host'],
        '-p', DB_CONFIG['port'],
        '-d', DB_CONFIG['name'],
        '-c', sql
    ]
    
    if quiet:
        cmd.extend(['-t', '-A'])  # 只输出数据，无表格格式
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()
    except FileNotFoundError:
        print_error("psql 命令未找到，请先安装 PostgreSQL 客户端")
        sys.exit(1)

def run_psql_file(file_path: str) -> Tuple[bool, str]:
    """
    执行psql脚本文件
    
    Args:
        file_path: SQL脚本文件路径
    
    Returns:
        (成功标志, 输出内容)
    """
    cmd = [
        'psql',
        '-U', DB_CONFIG['user'],
        '-h', DB_CONFIG['host'],
        '-p', DB_CONFIG['port'],
        '-d', DB_CONFIG['name'],
        '-f', file_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError:
        print_error("psql 命令未找到，请先安装 PostgreSQL 客户端")
        sys.exit(1)

def check_database_connection() -> bool:
    """检查数据库连接"""
    print_info("检查数据库连接...")
    success, output = run_psql_command("SELECT 1;", quiet=True)
    
    if success:
        print_success("数据库连接成功")
        return True
    else:
        print_error("无法连接到数据库")
        print(f"错误信息: {output}")
        return False

def check_table_exists() -> bool:
    """检查表是否存在"""
    print_header("验证1: 检查表是否存在")
    
    sql = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'rule_config_table'
    );
    """
    
    success, output = run_psql_command(sql, quiet=True)
    
    if success and 't' in output:
        print_success("表 rule_config_table 存在")
        return True
    else:
        print_error("表 rule_config_table 不存在")
        print_info("请先执行迁移脚本: database/migrations/002_create_rule_config_table.sql")
        return False

def test_initialization_data() -> bool:
    """测试初始化数据"""
    print_header("验证2: 执行初始化数据测试")
    
    file_path = "database/tests/test_rule_config_initialization.sql"
    
    if not os.path.exists(file_path):
        print_error(f"测试文件不存在: {file_path}")
        return False
    
    success, output = run_psql_file(file_path)
    
    if success:
        print_success("初始化数据测试通过")
        # 显示关键结果
        for line in output.split('\n'):
            if '🎉' in line or '✓' in line or '✗' in line:
                print(f"  {line}")
        return True
    else:
        print_error("初始化数据测试失败")
        print(output)
        return False

def test_unique_index() -> bool:
    """测试唯一索引"""
    print_header("验证3: 执行唯一索引测试")
    
    file_path = "database/tests/test_rule_config_unique_index.sql"
    
    if not os.path.exists(file_path):
        print_error(f"测试文件不存在: {file_path}")
        return False
    
    success, output = run_psql_file(file_path)
    
    if success:
        print_success("唯一索引测试通过")
        # 显示关键结果
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if '所有测试通过' in line or '唯一索引' in line and '工作正常' in line:
                # 显示最后几行总结
                for summary_line in lines[max(0, i-2):i+3]:
                    if summary_line.strip():
                        print(f"  {summary_line}")
                break
        return True
    else:
        print_error("唯一索引测试失败")
        print(output)
        return False

def check_record_count() -> bool:
    """检查记录数量"""
    print_header("验证4: 检查记录数量")
    
    sql = "SELECT COUNT(*) FROM rule_config_table;"
    success, output = run_psql_command(sql, quiet=True)
    
    if success:
        count = int(output.strip())
        if count == 6:
            print_success(f"记录数量正确: {count} 条")
            return True
        else:
            print_warning(f"记录数量异常: {count} 条（期望6条）")
            return False
    else:
        print_error("无法查询记录数量")
        return False

def check_enabled_rules() -> bool:
    """检查所有规则是否启用"""
    print_header("验证5: 检查所有规则是否启用")
    
    sql = "SELECT COUNT(*) FROM rule_config_table WHERE enabled = TRUE;"
    success, output = run_psql_command(sql, quiet=True)
    
    if success:
        count = int(output.strip())
        if count == 6:
            print_success(f"所有规则都已启用: {count} 条")
            return True
        else:
            print_warning(f"部分规则未启用: {count}/6")
            return False
    else:
        print_error("无法查询启用状态")
        return False

def check_uniqueness() -> bool:
    """检查rule_code唯一性"""
    print_header("验证6: 检查 rule_code 唯一性")
    
    sql = "SELECT COUNT(*) - COUNT(DISTINCT rule_code) FROM rule_config_table;"
    success, output = run_psql_command(sql, quiet=True)
    
    if success:
        duplicate_count = int(output.strip())
        if duplicate_count == 0:
            print_success("所有 rule_code 都是唯一的")
            return True
        else:
            print_error(f"发现重复的 rule_code: {duplicate_count} 个")
            return False
    else:
        print_error("无法检查唯一性")
        return False

def show_rules_overview():
    """显示规则配置概览"""
    print_header("验证7: 规则配置概览")
    
    sql = """
    SELECT 
        rule_code AS "规则代码",
        rule_name AS "规则名称",
        scheduled_time AS "执行时间",
        enabled AS "启用"
    FROM rule_config_table
    ORDER BY rule_code;
    """
    
    success, output = run_psql_command(sql, quiet=False)
    
    if success:
        print(output)
    else:
        print_error("无法查询规则配置")

def print_summary(results: dict):
    """打印验证总结"""
    print_header("验证总结")
    
    print("\n验收标准检查:")
    
    all_passed = all(results.values())
    
    if results.get('table_exists', False):
        print_success("标准1: 表结构符合设计文档定义")
    else:
        print_error("标准1: 表结构符合设计文档定义")
    
    if results.get('initialization_data', False) and results.get('record_count', False):
        print_success("标准2: 6条规则配置数据插入成功")
    else:
        print_error("标准2: 6条规则配置数据插入成功")
    
    if results.get('unique_index', False) and results.get('uniqueness', False):
        print_success("标准3: rule_code唯一约束生效")
    else:
        print_error("标准3: rule_code唯一约束生效")
    
    print()
    
    if all_passed:
        print(f"{Colors.GREEN}🎉 任务 1.2.4 验证完成！所有验收标准都已满足！{Colors.NC}")
    else:
        print(f"{Colors.RED}❌ 部分验证未通过，请检查上述测试结果{Colors.NC}")
    
    print("\n" + "=" * 50)
    
    return all_passed

def main():
    """主函数"""
    print_header("任务 1.2.4 快速验证 (Python版本)")
    
    print("\n数据库配置:")
    print(f"  - 主机: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  - 数据库: {DB_CONFIG['name']}")
    print(f"  - 用户: {DB_CONFIG['user']}")
    print()
    
    # 检查数据库连接
    if not check_database_connection():
        sys.exit(1)
    
    # 执行所有验证
    results = {}
    
    results['table_exists'] = check_table_exists()
    if not results['table_exists']:
        sys.exit(1)
    
    results['initialization_data'] = test_initialization_data()
    results['unique_index'] = test_unique_index()
    results['record_count'] = check_record_count()
    results['enabled_rules'] = check_enabled_rules()
    results['uniqueness'] = check_uniqueness()
    
    show_rules_overview()
    
    # 打印总结
    all_passed = print_summary(results)
    
    # 返回退出码
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n验证已取消")
        sys.exit(1)
    except Exception as e:
        print_error(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
