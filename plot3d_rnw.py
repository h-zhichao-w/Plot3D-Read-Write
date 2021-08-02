"""
__title__ = ''
__author__ = 'Hansen Wong // 王之超'
__time__ = 2021/7/31 10:56
__file__ = plot3d_rnw.py
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
             ┏┓    ┏┓
            ┏┛┻━━━┛ ┻┓
            ┃         ┃
            ┃  ┳┛  ┗┳  ┃
            ┃     ┻    ┃
            ┗━┓      ┏━┛
              ┃      ┗━━━┓
              ┃  神兽保佑  ┣┓
              ┃　永无BUG！ ┏┛
                ┗┓┓┏━┳┓┏┛
                 ┃┫┫  ┃┫┫
                 ┗┻┛  ┗┻┛
"""
import numpy as np
import sys
import struct

"""
Pay tribute to the writers of the existing plot3d repositories, they gave me a lot of inspiration, THANK YOU!
"""

# define the length of different types of variables
int_len = 4
float_len = 4
double_len = 8

class Block:
    def __init__(self, ID, JD, KD):
        """
        the number of points on the direction of i, j, and k
        """
        self.id = ID
        self.jd = JD
        self.kd = KD
        self.X = np.zeros(self.id)
        self.Y = np.zeros(self.jd)
        self.Z = np.zeros(self.kd)
        self.IBlank = np.array([])
        self.cor = np.array([])

    def setX(self, x_list):
        self.X = x_list

    def setY(self, y_list):
        self.Y = y_list

    def setZ(self, z_list):
        self.Z = z_list

    def setBlank(self, blank_list):
        self.IBlank = blank_list

    def setXYZ(self, x_list, y_list, z_list):
        self.X = x_list
        self.Y = y_list
        self.Z = z_list

    def to_cor(self):
        """
        the information has already saved in X, Y and Z, in the form of
            [
                [X]
                [Y]
                [Z]
            ]
        This function is intended to convert the coordinate information into the form
            [
                [X, Y]
            ]
        """
        temp = []
        for i in range(self.X.size):
            temp.append([self.X[i], self.Y[i]])
        self.cor = np.array(temp)
        print(self.cor.shape)
        print(self.cor)


class Mesh:
    def __init__(self, filename: str, dimension: int, accuracy = 2):
        """
        :param filename: the path of the mesh file (the file should be written in binary!!)
        :param dimension: the dimension of mesh file. 3 is recommended
        :param accuracy: 1 for single precision, 2 for double precision
        """
        self.DIM = dimension
        self.BlockNumber = 1
        self.block_list = np.array([])
        self.Block = []
        self.filename = filename
        if accuracy == 2:
            self.accuracy = [double_len, 'd']
        else:
            self.accuracy = [float_len, 'f']

    def MeshInit(self):
        """
        create the Block object according to each block in the mesh
        """
        for i in range(self.BlockNumber):
            block = Block(*self.block_list[3 * i : 3 * (i + 1)])
            self.Block.append(block)
        print('BLOCK: {}'.format(self.Block))

    def read(self):
        """
        read the following information:
            The number of block
            The form of blocks
        and save the coordinate information in the corresponding block object
        """
        with open(self.filename, 'rb') as mesh_file:
            b = mesh_file.read(int_len)
            self.BlockNumber = int.from_bytes(b, byteorder=sys.byteorder)
            print('The number of block is {}'.format(self.BlockNumber))

            b = []
            for i in range(self.BlockNumber):
                for j in range(self.DIM):
                    b.append(mesh_file.read(int_len))
                if self.DIM == 2:
                    b.append(1)
            block_list = np.array(
                [int.from_bytes(i, byteorder=sys.byteorder) for i in b]
            )
            self.block_list = block_list
            print('block_list is {}'.format(self.block_list))

            self.MeshInit()

            for block_index in range(self.BlockNumber):
                block = self.Block[block_index]
                point_num = block.id * block.jd * block.kd
                print('point number of Block{} is {}'.format(block_index, point_num))

                b = []
                for i in range(point_num):
                    b.append(mesh_file.read(self.accuracy[0]))
                x_list = np.array(
                    [struct.unpack(self.accuracy[1], im) for im in b]
                )
                x_list = x_list.reshape([len(x_list)])
                print('x_list of Block{} is {}, the shape is {}.'.format(block_index, x_list, x_list.shape))
                block.setX(x_list)

                b = []
                for i in range(point_num):
                    b.append(mesh_file.read(self.accuracy[0]))
                y_list = np.array(
                    [struct.unpack(self.accuracy[1], im) for im in b]
                )
                y_list = y_list.reshape([len(y_list)])
                print('y_list of Block{} is {}, the shape is {}.'.format(block_index, y_list, y_list.shape))
                block.setY(y_list)

                b = []
                for i in range(point_num):
                    b.append(mesh_file.read(self.accuracy[0]))
                z_list = np.array(
                    [struct.unpack(self.accuracy[1], im) for im in b]
                )
                z_list = z_list.reshape([len(z_list)])
                print('z_list of Block{} is {}, the shape is {}.'.format(block_index, z_list, z_list.shape))
                block.setZ(z_list)

                block.to_cor()

    def converge(self):
        """
        if the mesh contains more than one block, use this function to converge all the block.cor,
        and to create a matrix containing all the coordinate information in the form of [X, Y]
        """
        if self.BlockNumber > 1:
            temp = []
            for block in self.Block:
                for cor in block.cor:
                    temp.append(cor)
            self.converged_cor = np.array(temp)
        else: pass

class Field:
    def __init__(self, filename: str, dimension: int, accuracy = 1):
        """
        :param filename: the path of the field file (the file should be written in binary!!)
        :param dimension: the dimension of mesh file. 3 is recommended
        :param accuracy: 1 for single precision, 2 for double precision
        """
        self.DIM = dimension
        self.BlockNumber = 1
        self.block_list = np.array([])
        self.Block = []
        self.filename = filename
        self.VarNumber = 1
        if accuracy == 2:
            self.accuracy = [double_len, 'd']
        else:
            self.accuracy = [float_len, 'f']

    def FieldInit(self):
        """
        create the Block object according to each block in the mesh
        """
        for i in range(self.BlockNumber):
            block = Block(*self.block_list[3 * i : 3 * (i + 1)])
            self.Block.append(block)
        print('BLOCK: {}'.format(self.Block))

    def read(self):
        """
        read the following information:
            The number of block
            The form of blocks
            The number of variables
        and save the values of variables in the corresponding block object
        """
        with open(self.filename, 'rb') as field_file:
            b = field_file.read(int_len)
            self.BlockNumber = int.from_bytes(b, byteorder=sys.byteorder)
            print('The number of block is {}'.format(self.BlockNumber))

            b = []
            for i in range(self.BlockNumber):
                for j in range(self.DIM + 1):
                    if j == self.DIM:
                        self.VarNumber = int.from_bytes(field_file.read(int_len), byteorder=sys.byteorder)
                    else: b.append(field_file.read(int_len))
                if self.DIM == 2:
                    b.append(1)
            block_list = np.array(
                [int.from_bytes(i, byteorder=sys.byteorder) for i in b]
            )
            self.block_list = block_list
            print('block_list is {}'.format(self.block_list))
            print('VarNumber is {}'.format(self.VarNumber))

            self.FieldInit()

            for block_index in range(self.BlockNumber):
                block = self.Block[block_index]
                point_num = block.id * block.jd * block.kd
                print('point number of Block{} is {}'.format(block_index, point_num))

                block.var_list = np.zeros([self.VarNumber, point_num])
                for v in range(self.VarNumber):
                    b = []
                    for i in range(point_num):
                        b.append(field_file.read(self.accuracy[0]))
                    v_list = np.array(
                        [struct.unpack(self.accuracy[1], im) for im in b]
                    )
                    v_list = v_list.reshape([len(v_list)])

                    block.var_list[v] = v_list

                print('Block{}\'s variable list is {}, and the shape of it is {}.'.format(
                        block_index, block.var_list, block.var_list.shape
                    )
                )

    def write(self, mesh: Mesh, outcome: np.ndarray):
        """
        write a field file, with known number of variables, based on given mesh, and data(outcome)
        """
        with open(self.filename, 'wb') as field_file:
            field_file.write(mesh.BlockNumber.to_bytes(4, byteorder=sys.byteorder))

            for i in range(mesh.BlockNumber):
                for j in mesh.block_list[i * 3: i * 3 + 3]:
                    field_file.write(struct.pack('i', j))
                field_file.write(self.VarNumber.to_bytes(4, byteorder=sys.byteorder))

            for i in outcome:
                for j in i:
                    field_file.write((struct.pack(self.accuracy[1], j)))

    def converge(self):
        """
        if the field contains more than one block, use this function to converge all the block.var_list,
        and to create a matrix containing all values of all variables
        """
        if self.BlockNumber > 1:
            for i in range(self.BlockNumber):
                if i == 0:
                    self.converged_val = self.Block[i].var_list
                else:
                    self.converged_val = np.hstack((self.converged_val, self.Block[i].var_list))
        else: pass
