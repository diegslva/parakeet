
from ..ndtypes import type_conv
from ..syntax import TupleProj, get_type, ActualArgs


from helpers import unpack_closure

def linearize_arg_types(fn, args):

  """
  Given a function object which might be one of:
    (1) a closure type
    (2) the name of an untyped function
    (3) an untyped fn object
  and some argument types which might
    (1) a list
    (2) a tuple
    (3) an ActualArgs object
  linearize the argument types with respect to
  the untyped function's argument order and return
  both the untyped function and list of arguments
  """

  untyped_fundef, closure_args = unpack_closure(fn)
  if isinstance(args, (list, tuple)):
    args = ActualArgs(args)

  if len(closure_args) > 0:
    args = args.prepend_positional(closure_args)

  def keyword_fn(_, v):
    return type_conv.typeof(v)

  linear_args, extra = \
      untyped_fundef.args.linearize_values(args, keyword_fn = keyword_fn)
  return untyped_fundef, tuple(linear_args + extra)

def tuple_elts(tup):
  return [TupleProj(tup, i, t)
          for (i,t) in enumerate(tup.type.elt_types)]

def flatten_actual_args(args):
  if isinstance(args, (list,tuple)):
    return args
  assert isinstance(args, ActualArgs), \
      "Unexpected args: %s" % (args,)
  assert len(args.keywords) == 0
  result = list(args.positional)
  if args.starargs:
    result.extend(tuple_elts(args.starargs))
  return result

def linearize_actual_args(fn, args):
    untyped_fn, closure_args = unpack_closure(fn)
    if isinstance(args, (list, tuple)):
      args = ActualArgs(args)
    args = args.prepend_positional(closure_args)

    arg_types = args.transform(get_type)

    # Drop arguments that are assigned defaults,
    # since we're assuming those are set in the body
    # of the function
    combined_args = untyped_fn.args.linearize_without_defaults(args, tuple_elts)
    return untyped_fn, combined_args, arg_types