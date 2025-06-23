from typing import List
from slither import Slither
from slither.core.cfg.node import NodeType
from slither.core.declarations import FunctionContract
from slither.core.variables import StateVariable
import re

API_KEY = "HPXNN2GP4VFJIBD4USI8QJF6MFI75HRQZT"


def detect_low_level_creation(name: str, address: str, chain: str) -> bool:
    # 定位到工厂函数（使用了create / create2 内联汇编代码的函数）
    # 提取create / create2的返回值：deploymentAddress
    # 判断是否对deploymentAddress进行了一系列检查（论文）
    slither = Slither(target=address, etherscan_api_key=API_KEY, disable_solc_warnings=True)
    main_contract = slither.get_contract_from_name(name)
    assert len(main_contract) == 1
    main_contract = main_contract[0]
    for fn in main_contract.functions:
        deployed_address_var_name = ""
        for node in fn.nodes:
            if node.type == NodeType.ASSEMBLY and len(node.inline_asm) > 0:
                # 判断内部是否使用create / create2，并提取变量名
                pattern = r"([a-zA-Z_]\w*)\s*:=\s*(?:create|create2)\(.*\)"
                # re.search() 会在字符串中查找第一个匹配项
                match = re.search(pattern, node.inline_asm)
                if match:
                    deployed_address_var_name = match.group(1)
        if deployed_address_var_name:
            for node in fn.nodes:
                if node.is_conditional(False):
                    var_read = node.variables_read
                    for var in var_read:
                        if var.name == deployed_address_var_name:
                            return True
    return False


if __name__ == '__main__':
    name = "ImmutableCreate2Factory"
    address = "0x0000000000ffe8b47b3e2130213b802212439497"
    chain = ""
    is_factory = detect_low_level_creation(name, address, chain)
    print(is_factory)
