import sys
def dispatch(node, prefix = "", locals_dict = None):
  if locals_dict is None:
    last_frame = sys._getframe() 
    locals_dict = last_frame.f_back.f_locals
  node_type = node.__class__.__name__
  if len(prefix) > 0:
    fn_name = prefix + "_" + node_type
  else:
    fn_name = node_type
  if fn_name in locals_dict:
    return locals_dict[fn_name]()
  else:
    raise RuntimeError("Unsupported node type %s" % node_type)
