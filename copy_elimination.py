import names 

from syntax import Assign, Index, Slice, Var, Return 
from syntax_helpers import none, slice_none, zero_i64 

from core_types import NoneT, NoneType 
import array_type
from array_type import ArrayT 

from adverb_helpers import max_rank
from adverbs import Map 

import shape_inference

from transform import MemoizedTransform, apply_pipeline
from clone_function import CloneFunction

class PreallocateAdverbOutputs(MemoizedTransform):
  def niters(self, args, axis):
    max_rank = -1
    biggest_arg = None 
    for arg in args:
      r = self.rank(arg)
      if r > max_rank:
        max_rank = r 
        biggest_arg = arg
    return self.shape(biggest_arg, axis)
   
    
  
  def map_shape(self, maybe_clos, args, axis):
    fn = self.get_fn(maybe_clos)
    nested_abstract_shape = shape_inference.call_shape_expr(fn)
    closure_args = self.closure_elts(maybe_clos)
    nested_args = [self.index_along_axis(arg, axis, zero_i64) for arg in args]

    import shape_codegen 
    combined_args = closure_args + nested_args 
    inner_shape = shape_codegen.make_shape_expr(self, nested_abstract_shape, combined_args)
    niters = self.niters(args, axis)
    return self.concat_tuples(niters, inner_shape)
    
    
  def transform_Map(self, expr):
    if expr.out is None: 
      # transform the function to take an additional output parameter 
      output_shape = self.map_shape(expr.fn, expr.args, expr.axis)
      return_t = expr.fn.return_type 
      elt_t = return_t.elt_type if hasattr(return_t, 'elt_type') else return_t 
      expr.out = self.alloc_array(elt_t, output_shape) 
      expr.fn  =  make_output_storage_explicit(expr.fn)
    return expr 
  


class ExplicitOutputStorage(PreallocateAdverbOutputs):
  """
  Transform a function so that instead of returning a value
  it writes to an additional output parameter. 
  Should only be used as part of a recursive transform 
  by the parent class 'PreallocateAdverbOutputs'. 
  """
  def pre_apply(self, fn):
    output_name = names.fresh("output")
    output_t = fn.return_type
    
    if output_t.__class__ is ArrayT and output_t.rank > 0: 
      idx = self.tuple([slice_none] * output_t.rank)
      elt_t = output_t 

    else:
      idx = zero_i64
      elt_t = output_t 
      output_t = array_type.increase_rank(output_t, 1)
      
    
    self.output_type = output_t
    output_var = Var(output_name, type=output_t)
    self.output_lhs_index = Index(output_var, idx, type = elt_t)

    fn.return_type = NoneType  
    fn.arg_names = tuple(fn.arg_names) + (output_name,)
    fn.input_types = tuple(fn.input_types) + (output_t,)
    fn.type_env[output_name]  = output_t 
    self.return_none = Return(none)
    return fn 

  def transform_Return(self, stmt):
    if isinstance(stmt.value, Map):
      stmt.value.out = self.output_lhs_index 
    else:
      value = self.transform_expr(stmt.value)
      self.assign(self.output_lhs_index, value)
    return self.return_none
  
def make_output_storage_explicit(fn):
  
  return apply_pipeline(fn, [CloneFunction, ExplicitOutputStorage])
