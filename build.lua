#!/usr/bin/env texlua

-- Build script for jlreq-deluxe package

-- Identify the bundle and module
module = "jlreq-deluxe"
bundle = ""

-- Location of main directory: use Unix-style path separators
maindir = "."

-- Root directory of the TDS structure for the bundle/moduleto be installed into
tdsroot = "platex"

-- Files
binaryfiles      = {"*.pdf", "*.tfm", "*.vf", "*.zip"}
checksuppfiles   = {"texmf.cnf"}
cleanfiles       = {"*.log", "*.pdf", "*.zip"}
installfiles     = {"*.sty"}
sourcefiles      = {"*.sty"}
tagfiles         = {"*.sty"}
typesetfiles     = {"*.tex"}
typesetsuppfiles = {"texmf.cnf"}

-- Check engines
checkengines = {"ptex","uptex"}
stdengine    = "ptex"
checkformat  = "latex"

-- Executable
typesetexe = "platex"

-- Options pass to engine
checkopts   = " -kanji=utf8 -interaction=nonstopmode"
typesetopts = " -kanji=utf8 -interaction=nonstopmode"

checkruns   = 1
typesetruns = 3

-- Get the .tfm and .vf files in the right place
tdslocations =
  {
    "fonts/tfm/public/"..module.."/*.tfm",
    "fonts/vf/public/"..module.."/*.vf",
  }

-- Load the common build code
dofile("./build-config.lua")
dofile("./build-makejvf.lua")


-- Custom main function
function main(target, names)
  -- Add custom build target
  target_list.makejvf = {func = makejvf, desc = "Make japanese virtual fonts"}

  -- Customize build functions
  dvitopdf      = customize_dvitopdf(dvitopdf)
  typeset       = customize_typeset(typeset)
  install_files = customize_install_files(install_files)
  copyctan      = customize_copyctan(copyctan)

  -- Call standard main function
  stdmain(target, names)
end

-- Find and run the build system
kpse.set_program_name("kpsewhich")
if not release_date then
  dofile(kpse.lookup("l3build.lua"))
end
