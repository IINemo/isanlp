import argparse
import importlib

from isanlp.nlp_service_server import NlpServiceServer

parser = argparse.ArgumentParser(description='NLP service.')
parser.add_argument('-p', type = int, default = 3333, help = 'Port to listen.')
parser.add_argument('-t', type = int, default = 1, help = 'Number of workers.')
parser.add_argument('-m', type = str, default = 'isanlp.pipeline_default', help = 'Python module.')
parser.add_argument('-a', type = str, default= 'create_pipeline', help = 'Python function.')
args = parser.parse_args()

module_name = args.m 
creator_fn_name = args.a
port = args.p
nthreads = args.t

# object_str = """import {}
# {}.{}""".format(module_name, module_name, object_code)
# expr = compile(object_str, '<string>', 'exec')
# ppls = eval(expr)
# print(ppls)

creator_fn = getattr(importlib.import_module(module_name), creator_fn_name)
ppl = creator_fn(delay_init = True)
ppls = {ppl._name : ppl}

NlpServiceServer(ppls = ppls, port = port, max_workers = nthreads).serve()
