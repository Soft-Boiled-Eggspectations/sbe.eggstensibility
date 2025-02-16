from external_modules.module_b import execute

def execute_seq(msg: str) -> str:
    return execute(f"module_a: {msg}")
