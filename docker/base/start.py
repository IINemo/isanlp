from isanlp.nlp_service_server import NlpServiceServer 
import argparse


parser = argparse.ArgumentParser(description='NLP service.')
parser.add_argument('-p', type = int, default = 3333, help = 'Port to listen.')
parser.add_argument('-t', type = int, default = 1, help = 'Number of workers.')
parser.add_argument('-m', type = str, default = 'isanlp.pipeline_default', help = 'Python module.')
parser.add_argument('-a', type = str, default= 'PIPELINE_DEFAULT', help = 'Python object.')
args = parser.parse_args()

module_name = args.m 
object_code = args.a
port = args.p
nthreads = args.t

# object_str = """import {}
# {}.{}""".format(module_name, module_name, object_code)
# expr = compile(object_str, '<string>', 'exec')
# ppls = eval(expr)
# print(ppls)

def expand_ppl(ppl):
	res_dict = {k : v[0] for k, v in ppl.get_processors().items()}
	res_dict.update({ppl._name : ppl})
	return res_dict

ppls = eval("expand_ppl(__import__('importlib').import_module('{}').{})".format(module_name, object_code))

NlpServiceServer(ppls = ppls, port = port, max_workers = nthreads).serve()

