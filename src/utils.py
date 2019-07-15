def get_cli_parameters(args: list) -> list:
    all_args = []
    if len(args) > 1:
        print("Additional command-line parameters detected.")
        from .parameters import UserParameters
        params = UserParameters()
        for i, arg in enumerate(args):
            if arg in params.parameters:
                print(f"Command-line parameter detected - {arg[2:]}")
                all_args.append(arg[2:])
    return all_args