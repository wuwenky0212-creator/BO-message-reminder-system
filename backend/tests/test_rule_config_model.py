"""
Unit tests for RuleConfig model

测试RuleConfig模型类的所有功能，包括字段定义、索引、方法等。
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.rule_config import RuleConfig, Base


@pytest.fixture
def engine():
    """创建内存数据库引擎"""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """创建数据库会话"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestRuleConfigModel:
    """RuleConfig模型测试类"""
    
    def test_table_name(self):
        """测试表名是否正确"""
        assert RuleConfig.__tablename__ == 'rule_config_table'
    
    def test_columns_exist(self, engine):
        """测试所有列是否存在"""
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('rule_config_table')]
        
        expected_columns = [
            'id', 'rule_code', 'rule_name', 'scheduled_time', 'cron_expression',
            'target_roles', 'enabled', 'description', 'query_sql', 'timeout_seconds',
            'created_at', 'updated_at', 'updated_by'
        ]
        
        for col in expected_columns:
            assert col in columns, f"Column {col} not found in table"
    
    def test_primary_key(self, engine):
        """测试主键定义"""
        inspector = inspect(engine)
        pk = inspector.get_pk_constraint('rule_config_table')
        assert 'id' in pk['constrained_columns']
    
    def test_indexes_exist(self, engine):
        """测试索引是否存在"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes('rule_config_table')
        index_names = [idx['name'] for idx in indexes]
        
        expected_indexes = ['uk_rule_code', 'idx_enabled']
        
        for idx_name in expected_indexes:
            assert idx_name in index_names, f"Index {idx_name} not found"
    
    def test_unique_constraint_on_rule_code(self, engine):
        """测试rule_code唯一约束"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes('rule_config_table')
        
        # Find the uk_rule_code index
        uk_rule_code = next((idx for idx in indexes if idx['name'] == 'uk_rule_code'), None)
        assert uk_rule_code is not None
        # SQLite returns 1 for True, PostgreSQL returns True
        assert uk_rule_code['unique'] in (True, 1)
    
    def test_create_rule_config(self, session):
        """测试创建规则配置记录"""
        rule_config = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            enabled=True,
            description='每日下午14:30自动扫描所有处于"待审批/待复核"状态的交易记录',
            query_sql='SELECT COUNT(*) FROM trade_table WHERE approval_status IN (\'待审批\', \'待复核\')',
            timeout_seconds=5
        )
        
        session.add(rule_config)
        session.commit()
        
        assert rule_config.id is not None
        assert rule_config.rule_code == 'CHK_TRD_004'
        assert rule_config.rule_name == '当日交易未复核'
        assert rule_config.scheduled_time == '14:30'
        assert rule_config.cron_expression == '30 14 * * 1-5'
        assert rule_config.enabled is True
        assert rule_config.timeout_seconds == 5
    
    def test_duplicate_rule_code_fails(self, session):
        """测试重复的rule_code会失败"""
        rule_config1 = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            enabled=True,
            query_sql='SELECT COUNT(*) FROM trade_table',
            timeout_seconds=5
        )
        
        rule_config2 = RuleConfig(
            rule_code='CHK_TRD_004',  # Same rule_code
            rule_name='另一个规则',
            scheduled_time='15:00',
            cron_expression='0 15 * * 1-5',
            target_roles=['BO_Operator'],
            enabled=True,
            query_sql='SELECT COUNT(*) FROM another_table',
            timeout_seconds=10
        )
        
        session.add(rule_config1)
        session.commit()
        
        session.add(rule_config2)
        with pytest.raises(IntegrityError):
            session.commit()
    
    def test_query_by_rule_code(self, session):
        """测试按规则代码查询"""
        rule_config1 = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            enabled=True,
            query_sql='SELECT COUNT(*) FROM trade_table',
            timeout_seconds=5
        )
        rule_config2 = RuleConfig(
            rule_code='CHK_BO_001',
            rule_name='未证实匹配',
            scheduled_time='15:00',
            cron_expression='0 15 * * 1-5',
            target_roles=['BO_Operator'],
            enabled=True,
            query_sql='SELECT COUNT(*) FROM confirmation_table',
            timeout_seconds=5
        )
        
        session.add_all([rule_config1, rule_config2])
        session.commit()
        
        result = session.query(RuleConfig).filter_by(rule_code='CHK_TRD_004').first()
        assert result is not None
        assert result.rule_code == 'CHK_TRD_004'
        assert result.rule_name == '当日交易未复核'
    
    def test_query_enabled_rules(self, session):
        """测试查询启用的规则"""
        rule_config1 = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            enabled=True,
            query_sql='SELECT COUNT(*) FROM trade_table',
            timeout_seconds=5
        )
        rule_config2 = RuleConfig(
            rule_code='CHK_BO_001',
            rule_name='未证实匹配',
            scheduled_time='15:00',
            cron_expression='0 15 * * 1-5',
            target_roles=['BO_Operator'],
            enabled=False,
            query_sql='SELECT COUNT(*) FROM confirmation_table',
            timeout_seconds=5
        )
        
        session.add_all([rule_config1, rule_config2])
        session.commit()
        
        enabled_rules = session.query(RuleConfig).filter_by(enabled=True).all()
        assert len(enabled_rules) == 1
        assert enabled_rules[0].rule_code == 'CHK_TRD_004'
        
        disabled_rules = session.query(RuleConfig).filter_by(enabled=False).all()
        assert len(disabled_rules) == 1
        assert disabled_rules[0].rule_code == 'CHK_BO_001'
    
    def test_update_rule_config(self, session):
        """测试更新规则配置"""
        rule_config = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            enabled=True,
            query_sql='SELECT COUNT(*) FROM trade_table',
            timeout_seconds=5
        )
        
        session.add(rule_config)
        session.commit()
        
        # Update scheduled_time and timeout_seconds
        rule_config.scheduled_time = '15:00'
        rule_config.timeout_seconds = 10
        rule_config.updated_by = 'admin'
        session.commit()
        
        updated_rule = session.query(RuleConfig).filter_by(id=rule_config.id).first()
        assert updated_rule.scheduled_time == '15:00'
        assert updated_rule.timeout_seconds == 10
        assert updated_rule.updated_by == 'admin'
    
    def test_disable_rule(self, session):
        """测试禁用规则"""
        rule_config = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            enabled=True,
            query_sql='SELECT COUNT(*) FROM trade_table',
            timeout_seconds=5
        )
        
        session.add(rule_config)
        session.commit()
        
        assert rule_config.enabled is True
        
        # Disable the rule
        rule_config.enabled = False
        session.commit()
        
        updated_rule = session.query(RuleConfig).filter_by(id=rule_config.id).first()
        assert updated_rule.enabled is False
    
    def test_to_dict_method(self, session):
        """测试to_dict方法"""
        rule_config = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor', 'BO_Operator'],
            enabled=True,
            description='测试描述',
            query_sql='SELECT COUNT(*) FROM trade_table',
            timeout_seconds=5,
            updated_by='admin'
        )
        
        session.add(rule_config)
        session.commit()
        
        rule_dict = rule_config.to_dict()
        
        assert isinstance(rule_dict, dict)
        assert rule_dict['rule_code'] == 'CHK_TRD_004'
        assert rule_dict['rule_name'] == '当日交易未复核'
        assert rule_dict['scheduled_time'] == '14:30'
        assert rule_dict['cron_expression'] == '30 14 * * 1-5'
        assert rule_dict['target_roles'] == ['BO_Supervisor', 'BO_Operator']
        assert rule_dict['enabled'] is True
        assert rule_dict['description'] == '测试描述'
        assert rule_dict['query_sql'] == 'SELECT COUNT(*) FROM trade_table'
        assert rule_dict['timeout_seconds'] == 5
        assert rule_dict['updated_by'] == 'admin'
        assert 'id' in rule_dict
        assert 'created_at' in rule_dict
        assert 'updated_at' in rule_dict
    
    def test_repr_method(self, session):
        """测试__repr__方法"""
        rule_config = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            enabled=True,
            query_sql='SELECT COUNT(*) FROM trade_table',
            timeout_seconds=5
        )
        
        session.add(rule_config)
        session.commit()
        
        repr_str = repr(rule_config)
        assert 'RuleConfig' in repr_str
        assert 'CHK_TRD_004' in repr_str
        assert '当日交易未复核' in repr_str
        assert 'True' in repr_str
    
    def test_nullable_description(self, session):
        """测试description字段可为空"""
        rule_config = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            enabled=True,
            description=None,
            query_sql='SELECT COUNT(*) FROM trade_table',
            timeout_seconds=5
        )
        
        session.add(rule_config)
        session.commit()
        
        assert rule_config.description is None
    
    def test_nullable_updated_by(self, session):
        """测试updated_by字段可为空"""
        rule_config = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            enabled=True,
            query_sql='SELECT COUNT(*) FROM trade_table',
            timeout_seconds=5,
            updated_by=None
        )
        
        session.add(rule_config)
        session.commit()
        
        assert rule_config.updated_by is None
    
    def test_json_field_target_roles(self, session):
        """测试target_roles JSON字段"""
        roles = ['BO_Operator', 'BO_Supervisor', 'System_Admin']
        rule_config = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=roles,
            enabled=True,
            query_sql='SELECT COUNT(*) FROM trade_table',
            timeout_seconds=5
        )
        
        session.add(rule_config)
        session.commit()
        
        retrieved_rule = session.query(RuleConfig).filter_by(id=rule_config.id).first()
        assert retrieved_rule.target_roles == roles
    
    def test_default_enabled_value(self, session):
        """测试enabled字段的默认值"""
        rule_config = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            query_sql='SELECT COUNT(*) FROM trade_table',
            timeout_seconds=5
        )
        
        session.add(rule_config)
        session.commit()
        
        # Default should be True
        assert rule_config.enabled is True
    
    def test_default_timeout_seconds_value(self, session):
        """测试timeout_seconds字段的默认值"""
        rule_config = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            query_sql='SELECT COUNT(*) FROM trade_table'
        )
        
        session.add(rule_config)
        session.commit()
        
        # Default should be 10
        assert rule_config.timeout_seconds == 10
    
    def test_multiple_rules_with_different_schedules(self, session):
        """测试创建多个不同调度时间的规则"""
        rules = [
            RuleConfig(
                rule_code='CHK_TRD_004',
                rule_name='当日交易未复核',
                scheduled_time='14:30',
                cron_expression='30 14 * * 1-5',
                target_roles=['BO_Supervisor'],
                enabled=True,
                query_sql='SELECT COUNT(*) FROM trade_table',
                timeout_seconds=5
            ),
            RuleConfig(
                rule_code='CHK_BO_001',
                rule_name='未证实匹配',
                scheduled_time='15:00',
                cron_expression='0 15 * * 1-5',
                target_roles=['BO_Operator'],
                enabled=True,
                query_sql='SELECT COUNT(*) FROM confirmation_table',
                timeout_seconds=5
            ),
            RuleConfig(
                rule_code='CHK_SEC_003',
                rule_name='券持仓卖空缺口',
                scheduled_time='15:00',
                cron_expression='0 15,16 * * 1-5',
                target_roles=['BO_Supervisor'],
                enabled=True,
                query_sql='SELECT COUNT(*) FROM position_table',
                timeout_seconds=10
            )
        ]
        
        session.add_all(rules)
        session.commit()
        
        all_rules = session.query(RuleConfig).all()
        assert len(all_rules) == 3
        
        # Verify each rule
        rule_codes = [rule.rule_code for rule in all_rules]
        assert 'CHK_TRD_004' in rule_codes
        assert 'CHK_BO_001' in rule_codes
        assert 'CHK_SEC_003' in rule_codes
    
    def test_query_sql_text_field(self, session):
        """测试query_sql TEXT字段可以存储长SQL"""
        long_sql = """
        SELECT COUNT(*) 
        FROM trade_table t
        JOIN confirmation_table c ON t.id = c.trade_id
        WHERE t.approval_status IN ('待审批', '待复核')
        AND c.matching_status = '未匹配'
        AND t.trade_date = CURRENT_DATE
        """ * 10  # Make it longer
        
        rule_config = RuleConfig(
            rule_code='CHK_TRD_004',
            rule_name='当日交易未复核',
            scheduled_time='14:30',
            cron_expression='30 14 * * 1-5',
            target_roles=['BO_Supervisor'],
            enabled=True,
            query_sql=long_sql,
            timeout_seconds=5
        )
        
        session.add(rule_config)
        session.commit()
        
        retrieved_rule = session.query(RuleConfig).filter_by(id=rule_config.id).first()
        assert retrieved_rule.query_sql == long_sql
