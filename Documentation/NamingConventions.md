# Naming Conventions

    Pattern | char_type_name_location_[IDs]_class
    Example | soma_fk_shoulder_L_jnt 
              soma_bind_handDigit00_L_jnt
              soma_bind_joints_grp

Below is an expalanation of the naming conventions used inside of the tool. Honestly, it's more notes than documentation.

## Char

The name of the character. Added to support having multiple rigs in the scene. Planning to change this to a namespace to help with export and data reuse.

## Type

What purpose the node serves. Again, potatential change to Namespace for easier sharing of animation data.

- examples:
- bind
- blendshape
- ik
- fk
- proxy
- lod
- orient
- parent
- primary
- secondary
- diff
- refl

## Location

Where on the body it lies. Normally referred to as side, but left broad because I wanted to support human readible names if generated.
Naming ordered vertically then horizontally.

- **Left** | L  
- **Right** | R  
- **Middle or Medial** | M  
- **Front or Anterior** | F  
- **Anterior** | F  
- **Back or Posterior** | B  
- **Posterior** | B  
- **Top** | S  
- **Superior** | S *above*  
- **Bottom** | I  
- **Inferior** | I *below*  
- **Dorsal** | D [*back of torso, think shoulder blades and fins*]  
- **Ventral** | V [*front of torso, think pouch and utters*]  

in the event of multiple sets of limbs, like insects, they may also have an index

indexing starts with 0 represnting the most medial or the most superior.

In the event of hands and other extremities that do not fall perpendicular to the median line at rest, the numbering begins anterior and superior (so palm down, thumb is 0, pinky is 4, and palm forward thumb is 0, pinky is 4)

## Name

The anatomical bonne

Names are camelCased.
Use Generic names whenever possible.
*(finger00,finger01,finger02,finger03, etc instead of thumb, index, middle, ring.)* This will allow for uniformity across species and deviations.

## Class

The abreviated data type. Kept to 2-4 characters, consonants over vowels. If it's a multiple word thing, or a program specific format, include the

**Geometry** | geo  
**Joint** | jnt  
**Control** | cntl  
**Group** | grp  
**Material** | mtl  
**Light** | lt *TBD* maybe aLT or pLT, rLT sLT  
**Texture** | tex *or the specific channel it corresponds to*  
**Handle** | hndl  
**Shader Group** | sg (if applicable)  

## Numbering

always includes a leading 0 and have all numbers that belong to the same set be the same length. i.e. 0011, 0112, 0113 or 01, 02, 03, or 031, 043, 051.

Try to avoid adding to the front of a chain, but if necessary and renaming is not an option, go negative -001, -012,-031, etc

## Textures

The layer a texture corresponds to goes in the type segment. Again, try to keep to the same pattern as classes-- 2-4 characters when possible,

- albd  
- diff  
- refl  
- refr  
- cav  
- ao  
- mtlc  
- rgh  
- disp  
- *MSK  
