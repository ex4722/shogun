import binaryninja


""" 
Pick func, Resolve all symbols in it, recursive until hit base class, NON NamedTYpe??


Loop over everything:
    if enum resolve on top 
    if struct resolve its crap first 

"""
bv = binaryninja.open_view("new.bndb")
addr = 0x1178
curr_func = bv.get_functions_containing(addr)[0]

dyn = bv.types["Elf64_Dyn"]
s = bv.types["struct_2"]


def member_at_offset(structure : binaryninja.types.StructureType , offset: int):
    """ 
    member_at_offset(structure : binaryninja.types.StructureType , offset: int):
    
    Returns none instead of erroring when nothing found
    """
    try:
        return structure.member_at_offset(offset)
    except ValueError:
        return None


def patch_struct( structure : binaryninja.types.StructureType) -> binaryninja.types.StructureType:
    """
    patch_struct( structure : binaryninja.types.StructureType) -> binaryninja.types.StructureType:

    Returns a copy of structure that is padded with char[] for all non defined structures
    :param StructureType structure:
    """
    structure = structure.mutable_copy()
    i = 0
    times_padded = 1

    while i < structure.width:
        member = member_at_offset(structure, i)
        # Not defined, find how long undef chain is
        if member == None:
            null_c = 0
            while member_at_offset(structure,null_c + i) == None and (null_c + i ) < structure.width:
                null_c += 1
            structure.add_member_at_offset(f'BN_PADDING_{times_padded}', binaryninja.types.ArrayBuilder.create(binaryninja.types.CharType.create(), null_c ), i)
            i += null_c
            times_padded += 1

        else:
            i += member.type.width
    return structure.immutable_copy()


# bv = binaryninja.open_view("./chall")
# bv = binaryninja.open_view("chall.bndb")
a = 0

    match typed.type_class:
        case binaryninja.TypeClass.TypeReferenceClass:
            dep = [member.type for member in typed.members] 
            print("HI")
        case binaryninja.TypeClass.NamedTypeReferenceClass:
            print("HI")
        case binaryninja.TypeClass.EnumerationTypeClass:
            func_list.append(typed)
        case _:
            print("ELSE")


from binaryninja.types import NamedTypeReferenceType, StructureType,EnumerationType
def get_source(typedyped):
    name = typedyped.tokens[-1]
    type_str = ""
    if isinstance(typedyped, NamedTypeReferenceType):
        type_str = str(typedyped.get_lines(bv,str(name))[0])
    elif isinstance(typedyped,StructureType):
        type_str = str(typedyped.get_lines(bv,str(name))[0]).replace("__packed",'')
        type_str +="\n{\n"

        curr_off = 0
        pad_off = 1
        for member in typedyped.members:
            pad_size = member.offset-curr_off
            if pad_size !=0:
                type_str += f"\t char padding_{pad_off}[{pad_size}];\n"
                pad_off+=1
                curr_off+=pad_size
            type_str += "\t "+str(member)[1:].split(",")[0] +";\n"
            curr_off += member.type.width
        if curr_off < typedyped.width:
            pad_size = typedyped.width-curr_off
            type_str += f"\t char padding_{pad_off}[{pad_size}];\n"
        type_str+="};\n"
    elif isinstance(typedyped,EnumerationType):
        for x in typedyped.get_lines(bv,str(name)):
            # Check once? Too lazy :)
            type_str += str(x).split(":")[0] +"\n"    
    print(type_str)
    return type_str

func_list = []
a = 0
def resolve_function(typed):
    print(f"{typed.__str__()=}")
    global a
    match typed.type_class:
        case binaryninja.TypeClass.StructureTypeClass:
            dep = [member.type for member in typed.members]
            #print("StructTypeClass")
            print("="*100)
            for i in dep:
                resolve_function(i)
                print(f"Resolved {typed}")
            #func_list.append(typed)
                #print( i, i.type_class)
        case binaryninja.TypeClass.NamedTypeReferenceClass:
            # Resolve this guys crap
            a = typed
            resolve_function(typed.target(bv))
            #print(typed.named_type_class)
            #print(f"Resolved {typed}")
            #func_list.append(typed)

            #dep = [member.type for member in typed.members]
        case binaryninja.TypeClass.EnumerationTypeClass:
            pass
            #print(f"Resolved {typed}")
            #func_list.append(typed)
        case _:
            print("UNDEF")
            print(typed)

    if typed in func_list:
        print("ALREADY IN")
    else:
        func_list.append(typed)

for name, f in bv.types:
    resolve_function(f)

for i in func_list:
    get_source(i)

