import numpy as np
from plotly.subplots import make_subplots
import json
import plotly
import matplotlib.pyplot as plt
from scipy import signal, stats
import os
import pandas as pd
from py2neo import Graph, Node, NodeMatcher
from dtLib.BillOfMaterials import part_connections


class TimeHistory():
    def __repr__(self):
        msg = f"Time history generated from {self.source}"
        return(msg)

    def __str__(self):
        msg = f"Time history generated from {self.source}"
        return(msg)

    def __init__(self, t=np.arange(0, 5, 1/10240), t_u: str = 'seconds', x=np.zeros(51200), x_u: str = 'g', source: str = 'Experiment'):
        self.time = t
        self.time_units = t_u
        self.response = x
        self.response_units = x_u
        self.source = source

    def plot(self):
        """
        Create a JSON plot file for the time history via Plotly
        """
        fig = make_subplots(rows=1, cols=1, vertical_spacing=0.15)
        fig.add_scatter(x=self.time, y=self.response, mode='lines',
                        row=1, col=1, line={'color': 'black'})
        fig.update_xaxes(
            title_text=f"Time in {self.time_units}", titlefont=dict(size=15), row=1, col=1)
        fig.update_yaxes(title_text=f"Response in {self.response_units}", titlefont=dict(
            size=15), row=1, col=1)
        json_fig = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return(json_fig)  # Returns JSON figure file for DTOP

    def value(self, t=None):
        """
        Returns interpolated values at specified time
        """
        val = np.interp(t, self.time, self.response)
        return(val)

    def FFT(self):
        """
        Using generic Fast Fourier Transform, generates the frequency content of the time history
        """
        dt = self.time[1]-self.time[0]
        t = np.arange(self.time[0], self.time[-1], dt)
        y = self.value(t)
        resp = np.fft.fft(y)
        freq = np.fft.fftfreq(t.shape[-1], d=dt)
        resp, freq = resp[:int(len(resp)/2)], freq[:int(len(resp)/2)]
        self.fft_freq = freq
        self.fft_resp = resp

    def PSD(self):
        """
        Creates Power Spectral Density
        """
        try:
            self.psd_resp = (1/(2*len(self.fft_resp)**2)) * \
                np.abs(self.fft_resp)**2
            self.psd_freq = self.fft_freq
        except:
            self.FFT()
            self.psd_resp = (1/(2*len(self.fft_resp)**2)) * \
                np.abs(self.fft_resp)**2
            self.psd_freq = self.fft_freq

    def Hanning(self, size: float = 256):
        """
        If size is a decimal, takes int(floor(size)) as scaling size. Unknown units
        """
        dt = self.time[1]-self.time[0]
        t = np.arange(self.time[0], self.time[-1], dt)
        y = self.value(t)
        freq, Pxx = signal.welch(y, 1/dt, 'hann', size, scaling="spectrum")
        self.psd_freq = freq
        self.psd_resp = Pxx

    def plot_fft(self):
        """
        Checks to see if fft exists, then creates a JSON plot file for the FFT via Plotly
        """
        try:
            resp = np.abs(self.fft_resp)
            fig = make_subplots(rows=1, cols=1, vertical_spacing=0.15)
            fig.add_scatter(x=self.fft_freq, y=resp, mode='lines',
                            row=1, col=1, line={'color': 'black'})
            fig.update_xaxes(title_text=f"Frequency in 1/{self.time_units}",
                             type="log", titlefont=dict(size=15), row=1, col=1)
            fig.update_yaxes(title_text=f"Magnitude of Response in |{self.response_units}|", titlefont=dict(
                size=15), row=1, col=1)
            json_fig = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return(json_fig)
        except:
            print("FFT is not generated, please generate FFT data")

    def plot_psd(self):
        """
        Checks to see if psd exists, then reates a JSON plot file for the PSD via Plotly
        """
        try:
            resp = self.psd_resp
            fig = make_subplots(rows=1, cols=1, vertical_spacing=0.15)
            fig.add_scatter(x=self.psd_freq, y=resp, mode='lines',
                            row=1, col=1, line={'color': 'black'})
            fig.update_xaxes(title_text=f"Frequency in 1/{self.time_units}",
                             type="log", titlefont=dict(size=15), row=1, col=1)
            fig.update_yaxes(title_text=f"Power Spectral Density in {self.response_units}^2", titlefont=dict(
                size=15), row=1, col=1)
            json_fig = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return(json_fig)
        except:
            print("PSD is not generated, please generate PSD data")
    """
    
    Break for Temperary Modules
    
    
    
    """

    def plot_pyplot(self):
        """
        Temporary for Diagnostics - Shows pyplot version of the data
        """
        fig = plt.figure()
        plt.plot(self.time, self.response, 'k-x')
        plt.xlabel(f"Time in {self.time_units}")
        plt.ylabel(f"Response in {self.response_units}")
        plt.show()

    def plot_pyplot_fft(self):
        """
        Temporary for Diagnostics - Checks to see if fft exists, then plots
        """
        try:
            resp = np.abs(self.fft_resp)
            fig = plt.figure()
            plt.semilogy(self.fft_freq, resp, 'k-x')
            plt.xlabel(f"Frequency in 1/{self.time_units}")
            plt.ylabel(f"Magnitude of Response in |{self.response_units}|")
            plt.show()
        except:
            print("FFT is not generated, please generate FFT data")

    def plot_pyplot_psd(self):
        """
        Temporary for Diagnostics - Checks to see if psd exists, then plots
        """
        try:
            resp = self.psd_resp
            fig = plt.figure()
            plt.plot(self.psd_freq, resp, 'k-x')
            plt.xlabel(f"Frequency in 1/{self.time_units}")
            plt.ylabel(f"Power Spectral Density in {self.response_units}^2")
            plt.show()
        except:
            print("PSD is not generated, please generate PSD data")


class MODEL3DOF():
    def __repr__(self):  # return
        msg = f"3DOF model generated from {self.source}"
        return(msg)

    def __str__(self):  # Print
        msg = f"3DOF model generated from {self.source}"
        return(msg)

    def __init__(self, M=[5, 5, 5], mass_units: str = "kg", K=[40e3, 40e3, 40e3], stiff_units: str = "N/m", C=[6, 6, 6], damp_units: str = "Nm/s", dispersion=[0, 0, 0], dist: str = "normal", disp_units: str = "", source='user'):
        self.m1 = M[0]
        self.m2 = M[1]
        self.m3 = M[2]
        self.mass_units = mass_units
        self.k1 = K[0]
        self.k2 = K[1]
        self.k3 = K[2]
        self.stiff_units = stiff_units
        self.c1 = C[0]
        self.c2 = C[1]
        self.c3 = C[2]
        self.damp_units = damp_units
        self.disp_m = dispersion[0]
        self.disp_k = dispersion[1]
        self.disp_c = dispersion[2]
        self.disp_units = disp_units
        self.dist = dist
        self.source = source

    def matrix(self):  # return matrices
        """
        Generates 3x3 matrix representation of system. Output = M,K,C
        """
        M = np.array([[self.m1, 0, 0], [0, self.m2, 0], [self.m3, 0, 0]])
        K = np.array([[self.k1+self.k2, -self.k2, 0], [-self.k2,
                                                       self.k2+self.k3, -self.k3], [0, -self.k3, self.k3]])
        C = np.array([[self.c1+self.c2, -self.c2, 0], [-self.c2,
                                                       self.c2+self.c3, -self.c3], [0, -self.c3, self.c3]])
        return(M, K, C)

    def scalar(self):  # return scalar values
        """
        Returns scalar modular values, output = [m1,m2,m3], [k1,k2,k3], [c1,c2,c3]
        """
        M = [self.m1, self.m2, self.m3]
        K = [self.k1, self.k2, self.k3]
        C = [self.c1, self.c2, self.c3]
        return(M, K, C)

    def distribution(self):
        if self.dist == 'normal':
            m, k, c = self.scalar()
            M = stats.norm(loc=m, scale=3*[self.disp_m])
            K = stats.norm(loc=k, scale=3*[self.disp_k])
            C = stats.norm(loc=c, scale=3*[self.disp_c])
            return(M, K, C)

    def sample(self, N=10, seed=None):
        if seed is not None:
            np.random.seed(seed)
        M, K, C = self.distribution()
        return(M.rvs((N, 3)), K.rvs((N, 3)), C.rvs((N, 3)))

    def toJSON(self, path=""):
        """
        Converts object to JSON format. If path is empty, returns to memory, 
        otherwise, saves to file
        """
        try:
            parse = path.rsplit('.', 1)[1]
        except:
            parse = path
        if parse == "":  # create json object to memory
            file = json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)
            return(file)
        elif path == "prompt":  # prompt user
            print("Enter in File Path")
            path = input()
            try:
                parse = path.rsplit('.', 1)[1]
            except:
                parse = path
            if parse == "json":
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as fp:
                    json.dump(self, fp, default=lambda o: o.__dict__,
                              indent=4, separators=",:")
            else:
                filename = os.path.join(path, "Model.json")
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'w') as fp:
                    json.dump(self, fp, default=lambda o: o.__dict__,
                              indent=4, separators=",:")
        elif parse == "json":  # file is specified, write json to specified file
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as fp:
                json.dump(self, fp, default=lambda o: o.__dict__,
                          indent=4, separators=",:")
        else:  # file is not specified but folder is specified, create json file and write
            filename = os.path.join(path, "Model.json")
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as fp:
                json.dump(self, fp, default=lambda o: o.__dict__,
                          indent=4, separators=",:")

    def fromJSON(self, filepath=''):
        """
        Converts JSON file to 3DOF model
        """
        # Gather JSON file information
        if filepath == "":
            print("Enter in File Path")
            path = input()
            with open(path, 'r') as fp:
                File = json.load(fp)
        else:
            with open(filepath, 'r') as fp:
                File = json.load(fp)
        # Update Model from JSON
        keys = File.keys()
        for i in keys:
            setattr(self, i, File[i])

# Classes for creating a knowledge graph. See https://github.com/siwei0116/MscProject
# Node is a class from the library py2Neo
# A Node has a 'label' as the first argument, which will be defined as the 'nodetype'
# A node takes a dictionary(key-value pairs) to store properties


class myNode(Node):
    @classmethod
    def getsubClasses(cls):
        result = []
        for subclass in cls.__subclasses__():
            result.append(subclass)
        return result

    @classmethod
    def getNodeTypeList(cls):
        result = [a.nodeType for a in cls.getsubClasses()]
        return result

    @classmethod
    def getNodeDict(cls):
        dic = {}
        for a in cls.getsubClasses():
            for b in a.equivalence:
                dic[b] = a.nodeType
        return dic


class Component(myNode):  # Define a component node type
    identified_by = "Component_Number"  # The name of unique ID label for the node
    nodeType = "Component"
    # The equivalent expressions for the node
    equivalence = ["component", "part"]

    def __init__(self, componentNumber, name, cost, inventory, quantity, unit='EA'):
        self.nodeProperties = {}
        self.nodeProperties["Component_Number"] = componentNumber
        self.nodeProperties["Name"] = name
        self.nodeProperties["Cost"] = cost
        self.nodeProperties["Inventory"] = inventory
        self.nodeProperties["Quantity"] = inventory
        self.nodeProperties["Unit"] = unit
        super().__init__(self.nodeType, **self.nodeProperties)


class ComponentSystem(myNode):  # Define a system node type
    identified_by = "Name"
    nodeType = "System"
    equivalence = ["system", "subsystem"]

    def __init__(self, name):
        self.nodeProperties = {}
        self.nodeProperties['Name'] = name
        super().__init__(self.nodeType, **self.nodeProperties)


class Staff(myNode):  # Define a staff node type
    identified_by = "StaffID"
    nodeType = "Staff"
    equivalence = ["Employee"]

    def __init__(self, name, number):
        self.nodeProperties = {}
        self.nodeProperties["Name"] = name
        self.nodeProperties["StaffID"] = number
        super().__init__(self.nodeType, **self.nodeProperties)


class Supplier(myNode):  # Define a supplier node type
    identified_by = "SupplierID"
    nodeType = "Supplier"
    equivalence = ["supplier", "company", "seller"]

    def __init__(self, name, number):
        self.nodeProperties = {}
        self.nodeProperties["Name"] = name
        self.nodeProperties["SupplierID"] = number
        super().__init__(self.nodeType, **self.nodeProperties)


class Workstation(myNode):  # Define a workstation node type
    identified_by = "WorkstationID"
    nodeType = "Workstation"
    equivalence = ["workstation", "assembly position"]

    def __init__(self, workstation):
        self.nodeProperties = {}
        self.nodeProperties["WorkstationID"] = workstation
        super().__init__(self.nodeType, **self.nodeProperties)


class Assembly(myNode):  # Define an assembly node type, an assembly is a cluster of components (the bom structure is component-assembly-system-product)
    identified_by = "Name"
    nodeType = "Assembly"
    equivalence = ["module", "assembly"]

    def __init__(self, assembly):
        self.nodeProperties = {}
        self.nodeProperties["Name"] = assembly
        super().__init__(self.nodeType, **self.nodeProperties)


class Department(myNode):  # Define a department node type
    identified_by = "Name"
    nodeType = "Department"
    equivalence = ["department", "division"]

    def __init__(self, department):
        self.nodeProperties = {}
        self.nodeProperties["Name"] = department
        super().__init__(self.nodeType, **self.nodeProperties)


class Role(myNode):  # Define a Role(eg. Design engineer) node type
    identified_by = "Name"
    nodeType = "Role"
    equivalence = ['job', 'title', 'position', 'role']

    def __init__(self, role):
        self.nodeProperties = {}
        self.nodeProperties["Name"] = role
        super().__init__(self.nodeType, **self.nodeProperties)


class Product(myNode):  # Define a Product(eg. Model A) node type
    identified_by = "Name"
    nodeType = "Product"
    equivalence = ["model", "product"]

    def __init__(self, product, status):
        self.nodeProperties = {}
        self.nodeProperties["Name"] = product
        self.nodeProperties["Status"] = status
        super().__init__(self.nodeType, **self.nodeProperties)


class Entities():  # Define a class whcih can store lists of all node types
    # A class which contains lists of all nodes to be created in the knowledge graph
    list_component = []
    list_componentsystem = []
    list_staff = []
    list_supplier = []
    list_workstation = []
    list_assembly = []
    list_department = []
    list_staffRole = []
    list_products = []

    @classmethod
    def labeldic(self):
        '''return a dict for {Nodetype,Identity}'''
        mydic = {}
        for theNode in myNode.__subclasses__():
            mydic[theNode.nodeType] = theNode.identified_by
        return mydic

    # Transfer a node to a dictionary type (eg.{Label:"Component",Component_Number:"C0010001"})

    def nodeTodictionary(self, nodes):
        toDic = {}
        for k, v in nodes.items():
            toDic[k] = v
        return toDic

    # Transfer a node list to the dictionary(which contains a node as  dictionaries)
    def nodelistTOdictionary(self, nodelist):
        toDic = {}
        for node in nodelist:
            for k, v in node.items():
                if k in toDic and v not in toDic[k]:
                    toDic[k].append(v)
                else:
                    toDic[k] = [v]
        return toDic

    def NodeListtoJson(self):  # Export all nodes to json file
        toDic = {}
        toDic["Component"] = self.nodelistTOdictionary(
            self.list_component)
        toDic["Assembly"] = self.nodelistTOdictionary(self.list_assembly)
        toDic["System"] = self.nodelistTOdictionary(
            self.list_componentsystem)
        toDic["Department"] = self.nodelistTOdictionary(
            self.list_department)
        toDic["Products"] = self.nodelistTOdictionary(self.list_products)
        toDic["Staff"] = self.nodelistTOdictionary(self.list_staff)
        toDic["Role"] = self.nodelistTOdictionary(
            self.list_staffRole)
        toDic["Supplier"] = self.nodelistTOdictionary(self.list_supplier)
        toDic["Workstation"] = self.nodelistTOdictionary(
            self.list_workstation)
        with open("/Users/davidw/medjw/code/MscProject/data/nodeList.json", 'w') as f:
            json.dump(toDic, f)
        return toDic

    def addComponent(self, componentNumber, name, cost, inventory, quantity, unit):
        # add component as a Node object to the list_part list
        partNode = Component(componentNumber, name, cost,
                             inventory, quantity, unit)
        self.list_component.append(partNode)

    def addComponentSystem(self, name):
        # add system as a Node object to the list_part list
        componentSystemNode = ComponentSystem(name)
        self.list_componentsystem.append(componentSystemNode)

    def addStaff(self, name, staffID):
        # add staff as a Node object to the list_staff list
        staffNode = Staff(name, staffID)
        self.list_staff.append(staffNode)

    def addSupplier(self, name, supplierID):  # add a supplier node
        # add supplier as a Node object to the list_supplier list
        supplierNode = Supplier(name, supplierID)
        self.list_supplier.append(supplierNode)

    def addWorkstation(self, workstationID):
        # add workstation as a Node object to the workstation list
        workstationNode = Workstation(workstationID)
        self.list_workstation.append(workstationNode)

    def addAssembly(self, name):
        # add Assembly as a Node object to the Assembly list
        assemblyNode = Assembly(name)
        self.list_assembly.append(assemblyNode)

    def addDepartment(self, name):
        departmentNode = Department(name)
        self.list_department.append(departmentNode)

    def addStaffRole(self, name):
        # add job Role as a Node object to the job Role list
        staffroleNode = Role(name)
        self.list_staffRole.append(staffroleNode)

    def addProducts(self, name, status):
        productNode = Product(name, status)
        self.list_products.append(productNode)

    def extractComponentFromFile(self, datafile, systemName='Electric Motor Systems'):
        # extract all components information from a system part list, eg.Electric Motor System
        # print(f"extracting all component info of {systemName}.....")
        bom = pd.read_excel(
            datafile, index_col=None, sheet_name=systemName)
        part_numbers = bom["Component Number"].tolist()
        part_names = bom["Component Name"].tolist()
        part_costs = bom["Cost"].tolist()
        part_quantities = bom['Qta'].tolist()
        part_units = bom['Unit'].tolist()
        part_inventory = bom['Inventory'].tolist()
        assembly_name = list(set(bom["Assembly"].tolist()))

        for i in range(len(part_numbers)):
            self.addComponent(
                part_numbers[i], part_names[i], part_costs[i], part_inventory[i], part_quantities[i], part_units[i])

        for v in assembly_name:
            self.addAssembly(v)

    def extractComponentsystemFromFile(self, datafile, sheetname='Component System'):
        # extract all components system  information (ID and name) from a file
        # print("extracting all component system info.....")
        bom = pd.read_excel(
            datafile, index_col=None, sheet_name=sheetname)
        system_names = bom["Component System"].tolist()
        for i in range(len(system_names)):
            self.addComponentSystem(system_names[i])

    def extractStaffinofoFromFile(self, datafile, sheetname='Staff List'):
        # extract all Staff name and ID from the file
        # print("extracting all staff info.....")
        staffinfo = pd.read_excel(
            datafile, index_col=None, sheet_name=sheetname)
        staffNumbers = staffinfo["Staff Number"].tolist()
        StaffNames = staffinfo["Name"].tolist()
        Departments = list(set(staffinfo["Department"].tolist()))
        Roles = list(set(staffinfo["Responsibility/Role"].tolist()))
        for i in range(len(staffNumbers)):
            self.addStaff(StaffNames[i], staffNumbers[i])
        for v in Departments:
            self.addDepartment(v)
        for v in Roles:
            self.addStaffRole(v)

    def extractSupplierFromFile(self, datafile, sheetname='Supplier List'):
        # extract all Supplier name and ID from the file
        # print("extracting all supplier info.....")
        supplierinfo = pd.read_excel(
            datafile, index_col=None, sheet_name=sheetname)
        supplierNumber = supplierinfo["Supplier Code"].tolist()
        supplierName = supplierinfo["Supplier Name"].tolist()
        for i in range(len(supplierNumber)):
            self.addSupplier(supplierName[i], supplierNumber[i])

    def extractWorkstationFromFile(self, datafile, sheetname='Workstation List'):
        # extract all workstation name from the file
        # print("extracting all workstation info.....")
        workstationinfo = pd.read_excel(
            datafile, index_col=None, sheet_name=sheetname)
        workstation = workstationinfo["Workstation"].tolist()
        for i in range(len(workstation)):
            self.addWorkstation(workstation[i])

    def extractProductsFromFile(self, datafile, sheetname="Product Family"):
        # print("extracting product info....")
        productinfo = pd.read_excel(
            datafile, index_col=None, sheet_name=sheetname)
        product = productinfo["Product"].tolist()
        productStatus = productinfo["Status"].tolist()
        for i in range(len(product)):
            self.addProducts(product[i], productStatus[i])

    def extractAllNodes(self, datafile):
        self.extractComponentFromFile(datafile)
        self.extractComponentsystemFromFile(datafile)
        self.extractStaffinofoFromFile(datafile)
        self.extractSupplierFromFile(datafile)
        self.extractWorkstationFromFile(datafile)
        self.extractProductsFromFile(datafile)

    def allnodes(self):
        # Return all nodes of the object
        return self.list_assembly+self.list_component+self.list_componentsystem+self.list_department+self.list_staff+self.list_staffRole+self.list_supplier+self.list_workstation + self.list_products

    def assemblynodes(self):
        # Return assembly nodes of the object
        return self.list_assembly

    def componentnodes(self):
        # Return component nodes of the object
        return self.list_component


class Relation:
    # Define a relation class, which contains start node, start node type, endnode, endnode type, type of relation, and its property and direction
    def __init__(self, startnodetype, endnodetype, startnodeID, endnodeID, relationtype, bidirection=False, **karg):
        self.startnodeID = startnodeID
        self.endnodeID = endnodeID
        self.property = karg
        self.relationType = relationtype
        self.startnodeType = startnodetype
        self.endnodeType = endnodetype
        self.bidirection = bidirection

    @classmethod
    def getsubClasses(cls):  # get all subclasses of a class
        result = []
        for subclass in cls.__subclasses__():
            result.append(subclass)
        return result

    @classmethod
    def getRelationLabel(cls):  # get all labels of the relations
        result = [a.label for a in cls.getsubClasses()]
        return result

    @classmethod
    def getRelationDict(cls):  # get the {label:class} dictionary of a relation
        dic = {}
        for a in cls.getsubClasses():
            dic[a.label] = a
        return dic

    @classmethod
    # get the equivalence(synonym) dictionary for relations
    def getEquivalenceDict(cls):
        dic = {}
        for a in cls.getsubClasses():
            for b in a.equivalence:
                if b in dic:
                    dic[b].append(a.label)
                else:
                    dic[b] = [a.label]
        return dic

    @classmethod
    def getInverseDict(cls):  # get the inverse(antonym) dictionary for relations
        dic = {}
        for a in cls.getsubClasses():
            for b in a.inverse:
                if b in dic:
                    dic[b].append(a.label)
                else:
                    dic[b] = [a.label]
        return dic

    def __str__(self):
        if self.bidirection == False:
            return(f"Relation(({self.startnodeType}:{self.startnodeID})-({self.relationType}:{self.property})->({self.endnodeType}:{self.endnodeID})")
        else:
            return(f"Relation(({self.startnodeType}:{self.startnodeID})-({self.relationType}:{self.property})-({self.endnodeType}:{self.endnodeID})")

    def __repr__(self):
        if self.bidirection == False:
            return(f"Relation(({self.startnodeType}:{self.startnodeID})-({self.relationType}:{self.property})->({self.endnodeType}:{self.endnodeID})")
        else:
            return(f"Relation(({self.startnodeType}:{self.startnodeID})-({self.relationType}:{self.property})-({self.endnodeType}:{self.endnodeID})")


class fromStafftoDepartment(Relation):
    label = "works_in"
    startnodetype = "Staff"
    endnodetype = "Department"
    inverse = []
    equivalence = ['the personnel of', 'belong to', 'work for', 'work in']

    def __init__(self, staffID, department):
        super().__init__(self.startnodetype, self.endnodetype, staffID,
                         department, self.label)


class fromStafftoRole(Relation):
    label = "works_as"
    startnodetype = "Staff"
    endnodetype = "Role"
    inverse = ['have']
    equivalence = ['is responsible for', 'work as']

    def __init__(self, staffID, role):
        super().__init__(self.startnodetype, self.endnodetype, staffID,
                         role, self.label)


class fromAssemblytoComponent(Relation):
    label = "consists_of"
    startnodetype = "Assembly"
    endnodetype = "Component"
    inverse = ['composes']
    equivalence = ['consist of', 'compose of']

    def __init__(self, assembly, component_number):
        super().__init__(self.startnodetype, self.endnodetype, assembly,
                         component_number, self.label)


class fromAssemblytoSystem(Relation):
    label = "assemled_to"
    startnodetype = "Assembly"
    endnodetype = "System"
    inverse = ['assemble by', 'consist of', 'compose of', 'compose']
    equivalence = []

    def __init__(self, assembly, system):
        super().__init__(self.startnodetype, self.endnodetype, assembly,
                         system, self.label)


class fromSystemtoModel(Relation):
    label = "system_of"
    startnodetype = "System"
    endnodetype = "Product"
    inverse = ['assemble by', 'consist of', 'compose of', 'compose']
    equivalence = []

    def __init__(self, system, product):
        super().__init__(self.startnodetype, self.endnodetype, system, product, self.label)


class fromComponenttoStaff(Relation):
    label = "designed_by"
    startnodetype = "Component"
    endnodetype = "Staff"
    inverse = ['design', 'designed']
    equivalence = []

    def __init__(self, component, staff):
        super().__init__(self.startnodetype, self.endnodetype, component, staff, self.label)


class fromComponenttoSupplier(Relation):
    label = "supplied_by"
    startnodetype = "Component"
    endnodetype = "Supplier"
    inverse = ['supply']
    equivalence = ['purchase from', "supply by"]

    def __init__(self, component, supplier):
        super().__init__(self.startnodetype, self.endnodetype, component, supplier, self.label)


class fromComponenttoWorkstation(Relation):
    label = "Assemblied_At"
    startnodetype = "Component"
    endnodetype = "Workstation"
    inverse = ["assembly"]
    equivalence = ['assembly location of', 'assembly at']

    def __init__(self, component, workstation):
        super().__init__(self.startnodetype, self.endnodetype,
                         component, workstation, self.label)


class fromComponenttoComponent(Relation):
    label = "Connected_with"
    startnodetype = "Component"
    endnodetype = "Component"
    equivalence = ['linked_with']

    def __init__(self, component1, component2, connectionType):
        self.connectionType = connectionType
        super().__init__(self.startnodetype, self.endnodetype,
                         component1, component2, self.label, bidirection=True, connection_type=connectionType)

# The Relations class builds links between the entities defined in the Entities class based on the
# information given in the BoM.xlsx spreadsheet


class Relations:
    rel_stafftoDepartment = []
    rel_stafftoRole = []
    rel_assemblytoComponent = []
    rel_assemblytoSystem = []
    rel_systemtoModel = []
    rel_componentConnectedto = []
    rel_componentDesignedby = []
    rel_componentSuppliedby = []
    rel_componentAssembliedat = []

    def addStafftoDepartment(self, staffID, department):
        # extract staff-to-department relationship as (staffnumber,"belongs_to","department name") tuple
        # and append it to the list
        r = fromStafftoDepartment(staffID, department)
        self.rel_stafftoDepartment.append(r)

    def addStafftoRole(self, staffID, role):
        r = fromStafftoRole(staffID, role)
        self.rel_stafftoRole.append(r)

    def addAssemblytocomponent(self, assemblyName, componentNumber):
        r = fromAssemblytoComponent(assemblyName, componentNumber)
        self.rel_assemblytoComponent.append(r)

    def addcomponentDesignedby(self, componentNumber, staffNumber):
        r = fromComponenttoStaff(componentNumber, staffNumber)
        self.rel_componentDesignedby.append(r)

    def addcomponentSuppliedby(self, componentNumber, SupplierNumber):
        r = fromComponenttoSupplier(componentNumber, SupplierNumber)
        self.rel_componentSuppliedby.append(r)

    def addAssemblytoSystem(self, assemblyName, system):
        r = fromAssemblytoSystem(assemblyName, system)
        self.rel_assemblytoSystem.append(r)

    def addcomponentAssemby(self, componentNumber, workstationNumber):
        r = fromComponenttoWorkstation(componentNumber, workstationNumber)
        self.rel_componentAssembliedat.append(r)

    def addSystemtoModel(self, systemName, modelName):
        r = fromSystemtoModel(systemName, modelName)
        self.rel_systemtoModel.append(r)

    def addComponentConnection(self, component1, component2, connectionType):
        r = fromComponenttoComponent(component1, component2, connectionType)
        self.rel_componentConnectedto.append(r)

    def extractStaffRelation(self, datafile):
        # print("Extracting staff-department relationship from the file...")
        datafile = pd.read_excel(
            datafile, index_col=None, sheet_name="Staff List")
        staffNumber = datafile["Staff Number"].tolist()
        department = datafile["Department"].tolist()
        role = datafile["Responsibility/Role"].tolist()
        for i in range(len(staffNumber)):
            self.addStafftoDepartment(staffNumber[i], department[i])
            self.addStafftoRole(staffNumber[i], role[i])

    def extractcomponentRelation(self, datafile, systemName='Electric Motor Systems'):
        # print("Extracting component-assembly relationship from the file...")
        datafile = pd.read_excel(
            datafile, index_col=None, sheet_name=systemName)
        componentNumber = datafile["Component Number"].tolist()
        assembly = datafile["Assembly"].tolist()
        staff = datafile["Design Engineer"].tolist()
        supplier = datafile["Supplier"].tolist()
        workstation = datafile["Workstation"].tolist()

        for i in range(len(componentNumber)):
            self.addAssemblytocomponent(assembly[i], componentNumber[i])
            self.addcomponentDesignedby(componentNumber[i], staff[i])
            self.addcomponentSuppliedby(componentNumber[i], supplier[i])
            self.addcomponentAssemby(componentNumber[i], workstation[i])
        assembly = list(set(assembly))
        for i in range(len(assembly)):
            self.addAssemblytoSystem(assembly[i], systemName)

    def extractSystemtoModel(self, datafile, sheetname="Component System"):
        datafile = pd.read_excel(
            datafile, index_col=None, sheet_name=sheetname)
        systemName = datafile['Component System'].tolist()
        for v in systemName:
            self.addSystemtoModel(v, 'Model A')

    def extractComponentConnection(self, connectionList=part_connections.component_connection_list()):
        for connection_pair in connectionList:
            component1 = connection_pair[0]
            component2 = connection_pair[1]
            connectiontype = connection_pair[2]
            self.addComponentConnection(component1, component2, connectiontype)

    def extractAllRelation(self, datafile):
        self.extractStaffRelation(datafile)
        self.extractcomponentRelation(datafile)
        self.extractSystemtoModel(datafile)
        self.extractComponentConnection()

    def allRelations(self):
        return self.rel_assemblytoComponent+self.rel_assemblytoSystem +\
            self.rel_componentAssembliedat+self.rel_componentConnectedto +\
            self.rel_componentDesignedby+self.rel_componentSuppliedby +\
            self.rel_stafftoDepartment+self.rel_stafftoRole+self.rel_systemtoModel


class BuildGraph:
    # a BuldGraph class takes a list of nodes and edges
    def __init__(self, nodes, edges):
        # Connect to the Neo4j data base, the default passwrd for the local host is "123456"
        self.g = Graph("http://localhost:7474", auth=("neo4j", "123456"))
        # 'nodes' is a list of Node class defined in the entity.py
        self.nodes = nodes
        # 'edges' is a list of Relation class defined in relation.py
        self.edges = edges

    def createNodes(self, *nodes):
        # A funciotn to create nodes in the Neo4j graph database from the list of nodes
        for node in nodes:
            # this g.create function is from py2neo API to create one node in the Neo4j
            self.g.create(node)

    def deleteAll(self):
        # delete all nodes and edges in the Neo4j Graph database
        self.g.delete_all()

    def createRelations(self, *relations):
        '''create a relationship on the neo4j graph'''
        labeldict = Entities.labeldic()
        for r in relations:
            if r.bidirection == False:
                query = f"match(p:{r.startnodeType}) " +\
                    f"match (q:{r.endnodeType}) " +\
                    f"where p.{labeldict[r.startnodetype]} = '{r.startnodeID}' and q.{labeldict[r.endnodetype]} = '{r.endnodeID}' " +\
                    f"merge(p)-[r:{r.relationType}] -> (q) "
            else:
                query = f"match(p: {r.startnodeType}) " +\
                    f"match(q: {r.endnodeType}) " +\
                    f"where p.{labeldict[r.startnodetype]} = '{r.startnodeID}' and q.{labeldict[r.endnodetype]} = '{r.endnodeID}' " +\
                    f"merge(p)-[r:{r.relationType}]->(q)"
            for k, v in r.property.items():
                addQuery = f"set r.{k}='{v}'\n "
                query = query + " " + addQuery
            self.g.run(query)
            # print(query)

    def initialize(self):
        '''initialize the neo4j knowledge graph using the data(nodes and edges) assigned to the graph atrributes '''
        # clear the graph
        self.deleteAll()
        # create all nodes in the Neo4j database
        self.createNodes(*self.nodes.allnodes())
        # create edges in the Neo4j database TODO (to be refactored as the first two arguments are not needed)
        self.createRelations(*self.edges.allRelations())
