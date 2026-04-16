"""
运行所有测试脚本

此脚本会依次运行所有测试，并生成汇总报告。
"""

import subprocess
import sys
from datetime import datetime


def run_test(test_name: str, test_script: str) -> tuple:
    """运行单个测试脚本"""
    print(f"\n{'=' * 60}")
    print(f"运行测试: {test_name}")
    print(f"{'=' * 60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, test_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        
        return (result.returncode == 0, result.stdout)
    except subprocess.TimeoutExpired:
        print(f"✗ 测试超时（30秒）")
        return (False, "测试超时")
    except Exception as e:
        print(f"✗ 测试执行失败: {e}")
        return (False, str(e))


def main():
    """主函数"""
    print("=" * 60)
    print("消息表 (message_table) 测试套件")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 定义测试列表
    tests = [
        ("DDL 结构验证", "database/tests/test_message_table_ddl.py"),
        ("操作逻辑验证", "database/tests/test_message_table_operations.py")
    ]
    
    # 运行所有测试
    results = []
    for test_name, test_script in tests:
        success, output = run_test(test_name, test_script)
        results.append((test_name, success, output))
    
    # 生成汇总报告
    print("\n" + "=" * 60)
    print("测试汇总报告")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed
    
    print(f"\n总计: {len(results)} 个测试套件")
    print(f"✓ 通过: {passed}")
    print(f"✗ 失败: {failed}")
    
    print("\n详细结果:")
    for test_name, success, _ in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {status} - {test_name}")
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 最终结论
    if failed == 0:
        print("\n" + "=" * 60)
        print("🎉 所有测试都通过！")
        print("=" * 60)
        print("\n验收标准确认:")
        print("✓ 表结构符合设计文档定义")
        print("✓ 所有索引创建成功")
        print("✓ 可以正常插入和查询数据")
        print("\n任务 1.1.4 已成功完成！")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ 存在测试失败")
        print("=" * 60)
        print("\n请检查失败的测试并修复问题。")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
