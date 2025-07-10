# 测试文档

本文档描述了项目的测试框架和使用方法。

## 📋 测试概览

项目使用 `pytest` 作为测试框架，提供了完整的单元测试、集成测试和性能测试覆盖。

### 测试结构

```
tests/
├── __init__.py                 # 测试包初始化
├── conftest.py                 # pytest配置和fixture
├── test_schema.py              # 数据模式测试
├── test_adapter_manager.py     # 适配器管理器测试
├── test_adapters.py            # 适配器测试
├── test_quality_assessor.py    # 质量评估器测试
├── test_quality_rules.py       # 质量规则测试
├── test_integration.py         # 集成测试
├── test_cli.py                 # 命令行界面测试
└── test_data/                  # 测试数据
    ├── sample_watabou.json
    ├── sample_onepage.json
    └── sample_unified.json
```

## 🚀 快速开始

### 1. 安装测试依赖

```bash
# 使用测试脚本安装
python run_tests.py --install-deps

# 或手动安装
pip install pytest pytest-cov pytest-mock pytest-xdist
```

### 2. 检查测试环境

```bash
python run_tests.py --check-env
```

### 3. 运行所有测试

```bash
# 使用测试脚本
python run_tests.py

# 或直接使用pytest
python -m pytest tests/
```

## 🧪 测试类型

### 单元测试

测试各个模块的独立功能：

```bash
# 运行单元测试
python run_tests.py --type unit

# 或使用pytest标记
python -m pytest -m unit
```

### 集成测试

测试模块间的协作：

```bash
# 运行集成测试
python run_tests.py --type integration

# 或使用pytest标记
python -m pytest -m integration
```

### 性能测试

测试系统性能：

```bash
# 运行性能测试
python run_tests.py --type performance

# 或使用pytest标记
python -m pytest -m performance
```

### 快速测试

跳过慢速测试：

```bash
# 运行快速测试
python run_tests.py --type fast

# 或使用pytest标记
python -m pytest -m "not slow"
```

## 📊 测试覆盖率

生成测试覆盖率报告：

```bash
# 生成覆盖率报告
python run_tests.py --coverage

# 或直接使用pytest
python -m pytest --cov=src --cov-report=html --cov-report=term-missing
```

覆盖率报告将生成在 `htmlcov/` 目录中。

## 🔧 测试配置

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    performance: marks tests as performance tests
```

### conftest.py

包含所有测试的通用fixture：

- `project_root_path`: 项目根目录路径
- `test_data_dir`: 测试数据目录
- `sample_data_dir`: 样例数据目录
- `temp_dir`: 临时目录
- `sample_watabou_data`: Watabou格式样例数据
- `sample_onepage_data`: OnePage格式样例数据
- `unified_dungeon_data`: 统一格式样例数据
- `mock_adapter_manager`: 模拟的适配器管理器
- `mock_quality_assessor`: 模拟的质量评估器

## 📝 编写测试

### 测试文件命名

- 测试文件以 `test_` 开头
- 测试类以 `Test` 开头
- 测试方法以 `test_` 开头

### 测试类结构

```python
import pytest
from src.module import ClassToTest

class TestClassToTest:
    """测试ClassToTest类"""
    
    def test_method_name(self):
        """测试方法描述"""
        # 准备测试数据
        test_data = {...}
        
        # 执行被测试的方法
        result = ClassToTest.method(test_data)
        
        # 验证结果
        assert result is not None
        assert result.property == expected_value
```

### 使用Fixture

```python
def test_with_fixture(sample_watabou_data, temp_dir):
    """使用fixture的测试"""
    # 使用预定义的测试数据
    assert "title" in sample_watabou_data
    
    # 使用临时目录
    test_file = os.path.join(temp_dir, "test.json")
    # ... 测试逻辑
```

### 模拟外部依赖

```python
from unittest.mock import patch, MagicMock

def test_with_mock():
    """使用模拟的测试"""
    with patch('src.module.ExternalClass') as mock_class:
        mock_instance = MagicMock()
        mock_instance.method.return_value = "mocked_result"
        mock_class.return_value = mock_instance
        
        # 测试逻辑
        result = function_under_test()
        assert result == "mocked_result"
```

## 🎯 测试最佳实践

### 1. 测试命名

- 使用描述性的测试名称
- 测试名称应该说明测试的目的和预期结果

```python
def test_convert_watabou_to_unified_format_success():
    """测试Watabou格式成功转换为统一格式"""
    pass

def test_convert_invalid_data_returns_none():
    """测试无效数据转换返回None"""
    pass
```

### 2. 测试组织

- 按功能模块组织测试
- 使用测试类分组相关测试
- 使用fixture共享测试数据

### 3. 测试覆盖

- 测试正常情况
- 测试边界条件
- 测试错误情况
- 测试异常处理

### 4. 测试独立性

- 每个测试应该独立运行
- 避免测试间的依赖
- 使用临时文件和目录

### 5. 测试数据

- 使用最小化的测试数据
- 在 `test_data/` 目录中存放测试文件
- 使用fixture提供测试数据

## 🐛 调试测试

### 详细输出

```bash
python run_tests.py --verbose
```

### 运行特定测试

```bash
# 运行特定文件
python -m pytest tests/test_schema.py

# 运行特定测试类
python -m pytest tests/test_schema.py::TestUnifiedDungeonFormat

# 运行特定测试方法
python -m pytest tests/test_schema.py::TestUnifiedDungeonFormat::test_default_initialization
```

### 调试模式

```bash
# 在失败时进入调试器
python -m pytest --pdb

# 在第一个失败时停止
python -m pytest -x
```

## 📈 持续集成

### GitHub Actions

项目包含GitHub Actions工作流，自动运行测试：

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          python run_tests.py --coverage
```

### 本地CI

```bash
# 运行完整的CI检查
python run_tests.py --coverage --verbose
```

## 🔍 测试报告

### 生成HTML报告

```bash
python -m pytest --html=reports/test_report.html --self-contained-html
```

### 生成JUnit XML报告

```bash
python -m pytest --junitxml=reports/junit.xml
```

## 📚 相关文档

- [pytest官方文档](https://docs.pytest.org/)
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)
- [unittest.mock文档](https://docs.python.org/3/library/unittest.mock.html)

## 🤝 贡献测试

### 添加新测试

1. 在相应的测试文件中添加测试方法
2. 使用描述性的测试名称
3. 包含必要的断言
4. 添加测试文档字符串

### 测试新功能

1. 为新功能编写单元测试
2. 编写集成测试验证功能协作
3. 添加性能测试（如需要）
4. 更新测试覆盖率

### 测试维护

1. 定期运行完整测试套件
2. 保持测试覆盖率在80%以上
3. 及时修复失败的测试
4. 更新过时的测试 