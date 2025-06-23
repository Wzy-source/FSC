from typing import List
from slither import Slither
from slither.core.variables import StateVariable, Variable

API_KEY = "HPXNN2GP4VFJIBD4USI8QJF6MFI75HRQZT"


# 调用gigahorse，执行自定义的datalog文件，判断是否存在MissingImplementationValidation.csv文件
def detect_uncheck_implementation(name: str, address: str, chain: str) -> bool:
    # 构造命令，执行自定义factory.dl文件
    slither = Slither(target=address, etherscan_api_key=API_KEY, disable_solc_warnings=True)
    main_contract = slither.get_contract_from_name(name)
    assert len(main_contract) == 1, f"No Contract Or Multiple Contracts Named {name}"
    main_contract = main_contract[0]
    # 判断合约是否调用了两个函数“clone / cloneDeterministic”
    all_implementation_vars: List[Variable] = []
    for fn in main_contract.functions:
        for lib_call in fn.library_calls:
            if lib_call.function.canonical_name in ["Clones.clone(address)",
                                                    "Clones.cloneDeterministic(address,bytes32)"]:
                # 获取第一个address参数
                arg = lib_call.arguments[0]
                if arg.type.name == "address":
                    # 判断是否有对这个变量进行约束
                    all_implementation_vars.append(arg)

    # 收集所有的conditional_variables
    all_conditional_variables: List[Variable] = []
    for fn in main_contract.functions_and_modifiers:
        for node in fn.nodes:
            if node.is_conditional(False):
                all_conditional_variables.extend(node.variables_read)

    # 判断implementation合约地址变量是否被约束
    for imp_var in all_implementation_vars:
        if imp_var not in all_conditional_variables:
            return True

    return False


if __name__ == '__main__':
    name = "ERC721SeaDropCloneFactory"
    address = "0x00000000b8f8f18b708c8f7aa10f9ee7ea88049a"
    chain = ""
    res = detect_uncheck_implementation(name, address, chain)
    print(res)
