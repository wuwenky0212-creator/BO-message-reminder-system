#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本: 验证规则配置表初始化数据
任务: 1.2.3 - 初始化6条规则配置数据

功能:
- 验证6条规则配置记录是否正确插入
- 验证每条记录的字段值是否符合设计要求
- 验证规则代码唯一性约束
"""

import re
from typing import Dict, List, Any


class RuleConfigInitializationValidator:
    """规则配置初始化数据验证器"""
    
    # 预期的6条规则配置
    EXPECTED_RULES = {
        'CHK_TRD_004': {
            'rule_name': '当日交易未复核',
            'scheduled_time': '14:30',
            'cron_expression': '30 14 * * 1-5',
            'target_roles': ['BO_Supervisor'],
            'timeout_seconds': 5,
            'enabled': True
        },
        'CHK_BO_001': {
            'rule_name': '未证实匹配',
            'scheduled_time': '15:00',
            'cron_expression': '0 15 * * 1-5',
            'target_roles': ['BO_Operator'],
            'timeout_seconds': 5,
            'enabled': True
        },
        'CHK_CONF_005': {
            'rule_name': '未发证实报文',
            'scheduled_time': '15:30',
            'cron_expression': '30 15 * * 1-5',
            'target_roles': ['BO_Operator'],
            'timeout_seconds': 5,
            'enabled': True
        },
        'CHK_SW_002': {
            'rule_name': '未发收付报文',
            'scheduled_time': '15:00',
            'cron_expression': '0 15 * * 1-5',
            'target_roles': ['BO_Operator'],
            'timeout_seconds': 5,
            'enabled': True
        },
        'CHK_SETT_006': {
            'rule_name': '收付待审批',
            'scheduled_time': '16:00',
            'cron_expression': '0 16 * * 1-5',
            'target_roles': ['BO_Supervisor'],
            'timeout_seconds': 10,
            'enabled': True
        },
        'CHK_SEC_003': {
            'rule_name': '券持仓卖空缺口',
            'scheduled_time': '15:00',
            'cron_expression': '0 15,16 * * 1-5',
            'target_roles': ['BO_Supervisor'],
            'timeout_seconds': 10,
            'enabled': True
        }
    }
    
    def __init__(self, sql_file_path: str):
        """
        初始化验证器
        
        Args:
            sql_file_path: SQL迁移文件路径
        """
        self.sql_file_path = sql_file_path
        self.sql_content = self._read_sql_file()
        self.test_results = []
        
    def _read_sql_file(self) -> str:
        """读取SQL文件内容"""
        try:
            with open(self.sql_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"SQL文件不存在: {self.sql_file_path}")
    
    def _log_test(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        status = "✓" if passed else "✗"
        print(f"{status} {test_name}")
        if message:
            print(f"  {message}")
    
    def validate_insert_statement_exists(self) -> bool:
        """验证INSERT语句是否存在"""
        print("\n=== 验证INSERT语句存在性 ===")
        
        # 检查是否包含INSERT INTO语句
        has_insert = 'INSERT INTO rule_config_table' in self.sql_content
        self._log_test(
            "INSERT INTO语句存在",
            has_insert,
            "找到INSERT INTO rule_config_table语句" if has_insert else "未找到INSERT语句"
        )
        
        # 检查是否包含ON CONFLICT处理
        has_conflict_handling = 'ON CONFLICT' in self.sql_content
        self._log_test(
            "包含冲突处理(ON CONFLICT)",
            has_conflict_handling,
            "包含ON CONFLICT (rule_code) DO NOTHING" if has_conflict_handling else "缺少冲突处理"
        )
        
        return has_insert and has_conflict_handling
    
    def validate_rule_count(self) -> bool:
        """验证规则数量"""
        print("\n=== 验证规则数量 ===")
        
        # 统计VALUES子句中的记录数（通过统计rule_code出现次数）
        rule_code_pattern = r"'(CHK_[A-Z]+_\d+)'"
        rule_codes = re.findall(rule_code_pattern, self.sql_content)
        
        # 过滤掉注释中的rule_code
        insert_section = self._extract_insert_section()
        rule_codes_in_insert = re.findall(rule_code_pattern, insert_section)
        
        count = len(rule_codes_in_insert)
        expected_count = 6
        
        self._log_test(
            f"规则数量正确(期望{expected_count}条)",
            count == expected_count,
            f"实际找到{count}条规则: {', '.join(rule_codes_in_insert)}"
        )
        
        return count == expected_count
    
    def _extract_insert_section(self) -> str:
        """提取INSERT语句部分"""
        # 查找INSERT INTO到分号之间的内容
        pattern = r'INSERT INTO rule_config_table.*?;'
        match = re.search(pattern, self.sql_content, re.DOTALL)
        return match.group(0) if match else ""
    
    def validate_each_rule(self) -> bool:
        """验证每条规则的详细信息"""
        print("\n=== 验证每条规则的详细信息 ===")
        
        insert_section = self._extract_insert_section()
        all_passed = True
        
        for rule_code, expected_data in self.EXPECTED_RULES.items():
            print(f"\n检查规则: {rule_code}")
            
            # 验证rule_code存在
            has_rule_code = f"'{rule_code}'" in insert_section
            self._log_test(
                f"  {rule_code}: 规则代码存在",
                has_rule_code
            )
            all_passed = all_passed and has_rule_code
            
            # 验证rule_name
            has_rule_name = f"'{expected_data['rule_name']}'" in insert_section
            self._log_test(
                f"  {rule_code}: 规则名称正确",
                has_rule_name,
                f"期望: {expected_data['rule_name']}"
            )
            all_passed = all_passed and has_rule_name
            
            # 验证scheduled_time
            has_scheduled_time = f"'{expected_data['scheduled_time']}'" in insert_section
            self._log_test(
                f"  {rule_code}: 执行时间正确",
                has_scheduled_time,
                f"期望: {expected_data['scheduled_time']}"
            )
            all_passed = all_passed and has_scheduled_time
            
            # 验证cron_expression
            has_cron = f"'{expected_data['cron_expression']}'" in insert_section
            self._log_test(
                f"  {rule_code}: Cron表达式正确",
                has_cron,
                f"期望: {expected_data['cron_expression']}"
            )
            all_passed = all_passed and has_cron
            
            # 验证timeout_seconds
            has_timeout = str(expected_data['timeout_seconds']) in insert_section
            self._log_test(
                f"  {rule_code}: 超时时间正确",
                has_timeout,
                f"期望: {expected_data['timeout_seconds']}秒"
            )
            all_passed = all_passed and has_timeout
        
        return all_passed
    
    def validate_required_fields(self) -> bool:
        """验证必填字段是否都有值"""
        print("\n=== 验证必填字段 ===")
        
        insert_section = self._extract_insert_section()
        
        required_fields = [
            'rule_code',
            'rule_name',
            'scheduled_time',
            'cron_expression',
            'target_roles',
            'enabled',
            'query_sql',
            'timeout_seconds'
        ]
        
        all_passed = True
        for field in required_fields:
            # 检查字段是否在INSERT列定义中
            has_field = field in insert_section
            self._log_test(
                f"字段 {field} 已定义",
                has_field
            )
            all_passed = all_passed and has_field
        
        return all_passed
    
    def validate_json_format(self) -> bool:
        """验证JSON字段格式"""
        print("\n=== 验证JSON字段格式 ===")
        
        insert_section = self._extract_insert_section()
        
        # 检查target_roles的JSON格式
        json_patterns = [
            r'\["BO_Supervisor"\]',
            r'\["BO_Operator"\]'
        ]
        
        all_passed = True
        for pattern in json_patterns:
            has_pattern = re.search(pattern, insert_section) is not None
            self._log_test(
                f"JSON格式正确: {pattern}",
                has_pattern
            )
            all_passed = all_passed and has_pattern
        
        # 检查::JSON类型转换
        has_json_cast = '::JSON' in insert_section
        self._log_test(
            "包含JSON类型转换(::JSON)",
            has_json_cast
        )
        all_passed = all_passed and has_json_cast
        
        return all_passed
    
    def validate_business_rules(self) -> bool:
        """验证业务规则"""
        print("\n=== 验证业务规则 ===")
        
        all_passed = True
        
        # 验证1: CHK_TRD_004应该在14:30执行
        rule_004_time = "'CHK_TRD_004'" in self.sql_content and "'14:30'" in self.sql_content
        self._log_test(
            "CHK_TRD_004在14:30执行",
            rule_004_time,
            "交易复核提醒应在下午截账前执行"
        )
        all_passed = all_passed and rule_004_time
        
        # 验证2: CHK_SEC_003应该在15:00和16:00执行（cron: 0 15,16 * * 1-5）
        rule_003_cron = "'0 15,16 * * 1-5'" in self.sql_content
        self._log_test(
            "CHK_SEC_003在15:00和16:00执行",
            rule_003_cron,
            "券持仓卖空预警应执行两次"
        )
        all_passed = all_passed and rule_003_cron
        
        # 验证3: 所有规则都应该只在工作日执行（1-5）
        weekday_pattern = r'\* \* 1-5'
        has_weekday_restriction = len(re.findall(weekday_pattern, self.sql_content)) >= 6
        self._log_test(
            "所有规则限制在工作日执行",
            has_weekday_restriction,
            "Cron表达式应包含 1-5 (周一到周五)"
        )
        all_passed = all_passed and has_weekday_restriction
        
        # 验证4: 主管类规则应该分配给BO_Supervisor
        supervisor_rules = ['CHK_TRD_004', 'CHK_SETT_006', 'CHK_SEC_003']
        supervisor_count = 0
        for rule in supervisor_rules:
            if f"'{rule}'" in self.sql_content and '"BO_Supervisor"' in self.sql_content:
                supervisor_count += 1
        
        self._log_test(
            "主管类规则分配给BO_Supervisor",
            supervisor_count == len(supervisor_rules),
            f"找到{supervisor_count}/{len(supervisor_rules)}个主管规则"
        )
        all_passed = all_passed and (supervisor_count == len(supervisor_rules))
        
        return all_passed
    
    def run_all_validations(self) -> bool:
        """运行所有验证"""
        print("=" * 60)
        print("开始验证规则配置表初始化数据")
        print("=" * 60)
        
        validations = [
            self.validate_insert_statement_exists,
            self.validate_rule_count,
            self.validate_required_fields,
            self.validate_json_format,
            self.validate_each_rule,
            self.validate_business_rules
        ]
        
        all_passed = all([validation() for validation in validations])
        
        # 打印测试总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        passed_count = sum(1 for result in self.test_results if result['passed'])
        total_count = len(self.test_results)
        
        print(f"总计: {total_count} 项检查")
        print(f"✓ 通过: {passed_count}")
        print(f"✗ 失败: {total_count - passed_count}")
        
        if all_passed:
            print("\n🎉 所有验收标准都已满足！")
            print("✓ 6条规则配置数据已正确初始化")
            print("✓ 所有字段值符合设计要求")
            print("✓ 业务规则验证通过")
        else:
            print("\n⚠️  部分验证未通过，请检查以下失败项：")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ✗ {result['test']}")
                    if result['message']:
                        print(f"    {result['message']}")
        
        print("=" * 60)
        
        return all_passed


def main():
    """主函数"""
    import os
    
    # 获取SQL文件路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    sql_file = os.path.join(project_root, 'database', 'migrations', '002_create_rule_config_table.sql')
    
    # 运行验证
    validator = RuleConfigInitializationValidator(sql_file)
    success = validator.run_all_validations()
    
    # 返回退出码
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
