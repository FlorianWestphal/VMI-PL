VMI-PL
======

# Installation

## Required Software

Install Qemu-KVM and libvirt
``` shell
    sudo apt-get install qemu-kvm
```

## Qemu
1) Clone Qemu's git repository into a folder of your choice, e.g., `/opt/build/qemu`, further referenced as `QEMU`
``` shell
	mkdir $QEMU
	cd $QEMU
	git clone git://git.qemu-project.org/qemu.git
```

2) Check out supported revision from git repository
``` shell
    cd $KVM/qemu
    git checkout 1680d485777ecf436d724631ea8722cc0c66990e
```

3) Perform necessary changes on Qemu and build from source:
  1. apply VMI-PL patch for Qemu, which is located in the `back_end` folder under the root directory of the VMI-PL repository (the root directory is further referenced as `VMI-PL`), on the checked out `QEMU` folder, as shown below
  2. build patched Qemu
  
``` shell
    cd $QEMU/qemu
    patch -p1 < $VMI-PL/back_end/qemu.patch
    ./configure
    make
```

## KVM Kernel Module

1) Clone the git repository of the KVM kernel module into a folder of your choice, e.g., `/opt/build/kvm`, further referenced as `KVM`
``` shell
    mkdir $KVM
    cd $KVM
    git clone git://git.kiszka.org/kvm-kmod.git
```

2) Check out supported revision from git repository
``` shell
    cd $KVM/kvm-kmod
    git checkout 42c01897781bcb5a4ac7707b350d98348549e663
```

3) Load the corresponding linux submodule, as described here: [kvm-kmod readme](http://git.kiszka.org/?p=kvm-kmod.git;a=blob;f=README)
``` shell
    cd $KVM/kvm-kmod
    git submodule init
    git submodule update
```

4) Perform necessary changes on the KVM kernel module:

  1. apply VMI-PL patch, which is located in the `back_end` folder under the root directory of the VMI-PL repository (the root directory is further referenced as `VMI-PL`), on the checked out `KVM` folder, as shown below
  2. copy the VMI-PL header file, which is also located in the `back_end` folder, into following folder: `$KVM/kvm-kmod/linux/arch/x86/kvm/`
  3. apply additional patch from the `back_end` folder, if you are running on Linux kernel version 3.2

``` shell
    cd $KVM/kvm-kmod/linux
    patch -p1 < $VMI-PL/back_end/vmipl.patch
    cp $VMI-PL/back_end/vmi_pl.h arch/x86/kvm/
    # additional patch for Linux kernel version 3.2
    patch -p1 < $VMI-PL/back_end/external-module-compat-comm_h.patch
```

5) Build and install new KVM kernel module

``` shell
    cd $KVM/kvm-kmod
    ./configure
    make sync
    make
    sudo rmmod kvm_intel
    sudo rmmod kvm
    sudo insmod ./x86/kvm.ko
    sudo insmod ./x86/kvm-intel.ko
```

# Usage

1) Start VMI-PL execution environment, which is located in the `front_end` folder under the root directory of the VMI-PL repository, further referenced as `VMI-PL` (provide path to custom build qemu version (in this case: `$QEMU/qemu/x86_64-softmmu/qemu-system-x86_64`), if it cannot be run using the `qemu` command)

``` shell
    sudo $VMI-PL/front_end/server.py -s $QEMU/qemu/x86_64-softmmu/qemu-system-x86_64 &
```

2) Configure and start virtual machine, which should be monitored:

  1. create VMI-PL script file in a location of your choice, e.g., /opt/vmi-pl/test_script, further referenced as `SCRIPT_LOC`
  2. create virtual machine description file for qemu (the location of this file is further referenced as `VM_DESC_LOC`)
  3. start VMI-PL client, which is also located in the `front_end` folder, as shown below

``` shell
    $VMI-PL/front_end/client.py --start $VM_DESC_LOC $SCRIPT_LOC
```

**Note:** It must be possible to start the virtual machine from the provided virtual machine description file using qemu, as shown below

``` shell
    qemu -readconfig $VM_DESC_LOC
```

3) Reconfigure virtual machine (not yet implemented):

  1. read virtual machine id from the output of the VMI-PL client when the virtual machine was started (further referenced as `VM_ID`)
  2. write VMI-PL reconfiguration script and place it at a location of your choice (further referenced as `SCRIPT_LOC`)

``` shell
    $VMI-PL/front_end/client.py --reconfig $VM_ID $SCRIPT_LOC
```

# Examples

Several simple VMI-PL example scripts can be found in the `examples` folder under the root directory of the VMI-PL repository. These scripts use VMI-PL to retrieve following information from the guest operating system.

* network traffic to and from the virtual machine (`network_monitoring`)
* performed system calls (`process_execution_monitoring`)
* a list of running processes, whenever a process is terminated (`process_list`)
* scheduling and termination of a process (`process_life_cycle_monitoring`)

**Note:** The configuration of these scripts was tested for a virtual maching running Ubuntu 12.04 with a 32-bit Linux kernel version 3.2.0, which was started using the Qemu configuration script found in the `examples` folder (`ubuntu_12_04.cfg`)

