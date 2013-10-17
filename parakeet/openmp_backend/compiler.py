from ..c_backend import PyModuleCompiler

class MulticoreCompiler(PyModuleCompiler):
  
  def __init__(self, *args, **kwargs):
    PyModuleCompiler.__init__(self, *args, **kwargs)
    self.add_compile_flag("-fopenmp")
    self.add_link_flag("-fopenmp")
    self.parfor_counter = 0
    
  def visit_ParFor(self, stmt):
    
    bounds = self.tuple_to_var_list(stmt.bounds)
    loop_var_names = ["i", "j", "k", "l", "ii", "jj", "kk", "ll"]
    n_vars = len(bounds)
    assert n_vars <= len(loop_var_names)
    loop_vars = [self.fresh_var("int64_t", loop_var_names[i]) for i in xrange(n_vars)]
    
    self.parfor_counter += 1  
    fn_name = self.get_fn(stmt.fn)
    closure_args = self.get_closure_args(stmt.fn)
    combined_args = tuple(closure_args) + tuple(loop_vars)
    arg_str = ", ".join(combined_args)
    body = "%s(%s);" % (fn_name, arg_str)
    loops = self.build_loops(loop_vars, bounds, body)
    self.parfor_counter -= 1 
    if self.parfor_counter == 0:  
      release_gil = "\nPy_BEGIN_ALLOW_THREADS\n"
      acquire_gil = "\nPy_END_ALLOW_THREADS\n"  
      omp = "#pragma omp parallel for collapse(%d) private(%s)" % \
        (len(bounds), ", ".join(loop_vars))
      return release_gil + omp + loops + acquire_gil    
    else:
      return loops 
     
  def visit_IndexReduce(self, expr):
    assert False, "IndexReduce needs impl" 
  
  def visit_IndexScan(self, expr):
    assert False, "IndexScan needs impl"
  
  def visit_Map(self, expr):
    assert False, "Map should have been lowered into ParFor by now: %s" % expr 
  
  def visit_OuterMap(self, expr):
    assert False, "OuterMap should have been lowered into ParFor by now: %s" % expr 
  
  def visit_Reduce(self, expr):
    assert False, "Reduce should have been lowered into ParFor by now: %s" % expr 
  
  def visit_Scan(self, expr):
    assert False, "Scan should have been lowered into ParFor by now: %s" % expr
    
  def visit_IndexMap(self, expr):
    assert False, "IndexMap should have been lowered into ParFor by now: %s" % expr 
  
