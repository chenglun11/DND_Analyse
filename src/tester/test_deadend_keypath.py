import os
import json
import pytest
from src.quality_assessor import DungeonQualityAssessor

# 批量测试用例目录
TEST_DIR = 'output/batch_test'

# 只测试这两个新规则
TARGET_RULES = {'dead_end_ratio', 'key_path_length'}

@pytest.mark.parametrize('filename', [f for f in os.listdir(TEST_DIR) if f.endswith('.json')])
def test_deadend_and_keypath(filename):
    path = os.path.join(TEST_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assessor = DungeonQualityAssessor()
    result = assessor.assess_quality(data)
    # 检查新规则分数和细节都能正常输出
    print(f'\n==== {filename} ====')
    for rule in TARGET_RULES:
        assert rule in result['scores'], f"{rule} not in scores for {filename}"
        assert rule in result['details'], f"{rule} not in details for {filename}"
        # 分数应在0~1之间
        score = result['scores'][rule]
        assert 0.0 <= score <= 1.0, f"{rule} score out of range in {filename}: {score}"
        # 细节应有关键字段
        detail = result['details'][rule]
        assert isinstance(detail, dict), f"{rule} detail not dict in {filename}"
        print(f'{rule}: score={score}, detail={detail}') 