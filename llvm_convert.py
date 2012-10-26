from core_types import FloatT, SignedT, UnsignedT, BoolT, IntT
from llvm_types import int1_t, int8_t, llvm_value_type 
from llvm_helpers import zero 

import llvm.core as llcore 

def to_bit(llvm_value, builder):
  
  llvm_t = llvm_value.type
  print llvm_value, llvm_t 
   
  if llvm_t == int1_t:
    return llvm_value 
  if isinstance(llvm_t, llcore.IntegerType):
    return builder.icmp(llcore.ICMP_NE, llvm_value, zero(llvm_t), "ne_zero")
  else:
    return builder.fcmp(llcore.FCMP_ONE, llvm_value, zero(llvm_t), "ne_zero")

def from_bit(llvm_value, new_ptype, builder):
  dest_llvm_type = llvm_value_type(new_ptype)
  one = llcore.Constant(dest_llvm_type, 1.0 if isinstance(new_ptype, FloatT) else 1)
  zero = llcore.Constant(dest_llvm_type, 0.0 if isinstance(new_ptype, FloatT) else 0)
  return builder.select(llvm_value, one, zero, "%s.cast.%s" % (llvm_value.name, new_ptype))


def to_bool(llvm_value, old_ptype, builder):
  """
  bools are stored as bytes, if you need to use a boolean
  value for control flow convert it to a bit instead
  """
  bit = to_bit(llvm_value, builder)
  return builder.zext(bit, int8_t, "bool_val")

def from_float(llvm_value, new_ptype, builder):
  """Convert from an LLVM float value to some other LLVM scalar type"""
  dest_llvm_type = llvm_value_type(new_ptype)
  dest_name = "%s.cast_%s" % (llvm_value.name, new_ptype)
  
  
  if isinstance(new_ptype, FloatT):
    nbytes = llvm_value.type.width 
    if nbytes <= new_ptype.nbytes():
      return builder.fpext(llvm_value, dest_llvm_type, dest_name)
    else:
      return builder.fptrunc(llvm_value, dest_llvm_type, dest_name)
  elif isinstance(new_ptype, SignedT):
    return builder.fptosi(llvm_value, dest_llvm_type, dest_name)
  elif isinstance(new_ptype, UnsignedT):
    return builder.fptoui(llvm_value, dest_llvm_type, dest_name)
  else:
    return to_bool(llvm_value, builder)
    



def from_signed(llvm_value, new_ptype, builder):
  """Convert from an LLVM float value to some other LLVM scalar type"""
  

  dest_llvm_type = llvm_value_type(new_ptype)
  dest_name = "%s.cast_%s" % (llvm_value.name, new_ptype)
  
  
  if isinstance(new_ptype, FloatT):
    return builder.sitofp(llvm_value, dest_llvm_type, dest_name)
  elif isinstance(new_ptype, BoolT):
    return to_bool(llvm_value, builder)
  else:
    assert isinstance(new_ptype, IntT)
    nbits = llvm_value.type.width
    nbytes = nbits / 8 
   
    if nbytes == new_ptype.nbytes:
      return builder.bitcast(llvm_value, dest_llvm_type, dest_name)
    elif nbytes < new_ptype.nbytes:
      return builder.zext(llvm_value, dest_llvm_type, dest_name)
    else:
      return builder.trunc(llvm_value, dest_llvm_type, dest_name)
    

def from_unsigned(llvm_value, new_ptype, builder):

  """Convert from an LLVM float value to some other LLVM scalar type"""
  dest_llvm_type = llvm_value_type(new_ptype)
  dest_name = "%s.cast_%s" % (llvm_value.name, new_ptype)
  
  if isinstance(new_ptype, FloatT):
    return builder.uitofp(llvm_value, dest_llvm_type, dest_name)
  elif isinstance(new_ptype, BoolT):
    return to_bool(llvm_value, builder)
  else:
    assert isinstance(new_ptype, IntT)
    nbytes = llvm_value.type.width / 8 
     
    if nbytes == new_ptype.nbytes:
      return builder.bitcast(llvm_value, dest_llvm_type, dest_name)
    elif nbytes < new_ptype.nbytes:
      return builder.zext(llvm_value, dest_llvm_type, dest_name)
    else:
      return builder.trunc(llvm_value, dest_llvm_type, dest_name)
  

  
def convert(llvm_value, old_ptype, new_ptype, builder):
  """
  Given an LLVM value and two parakeet types, generate the instruction
  to perform the conversion
  """
  if old_ptype == new_ptype:
    return llvm_value 
    
  if isinstance(old_ptype, FloatT):    
    return from_float(llvm_value, new_ptype, builder)
  elif isinstance(old_ptype, SignedT):
    return from_signed(llvm_value, new_ptype, builder)
     
  else:
    assert isinstance(old_ptype, (BoolT, UnsignedT))
    return from_unsigned(llvm_value, new_ptype, builder)
  