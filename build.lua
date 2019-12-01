#!/usr/bin/env texlua

-- Build script for jlreq-deluxe package

-- Identify the bundle and module
module = "jlreq-deluxe"
bundle = ""

-- Location of main directory: use Unix-style path separators
maindir = "."
docfiledir = maindir
testsuppdir = maindir

-- Check engines
stdengine = "ptex"
checkengines = {"ptex","uptex"}
checkformat = "latex"
checkopts = "-kanji=utf8 -interaction=nonstopmode"

-- Non-standard settings
checkfiles   = { }
cleanfiles   = {"*.tfm", "*.vf", "*.log", "*.pdf", "*.zip"}
docfiles     = {"jlreq-deluxe.tex"}
installfiles = {"*.tfm", "*.vf", "*.sty"}
sourcefiles  = {"*.tfm", "*.vf", "*.sty"}
tagfiles     = {"jlreq-deluxe.sty"}
typesetfiles = {"jlreq-deluxe.tex"}
typesetskipfiles = { }
typesetruns      = 3
unpackfiles      = { }

checkdeps   = { }
typesetdeps = { }
unpackdeps  = { }

typesetexe  = "platex"

-- Get the .tfm and .vf files in the right place
tdslocations =
  {
    "fonts/tfm/public/jlreq-deluxe/*.tfm",
    "fonts/vf/public/jlreq-deluxe/*.vf",
    "tex/platex/jlreq-deluxe/*.sty",
  }

-- Load the common build code
dofile("./build-vfcopy.lua")
dofile("./build-config.lua")

function main(target, names)
  target_list.vfcopy = {func = vfcopy, desc = "Copy virtual fonts"}
  stdmain(target, names)
end

-- Find and run the build system
kpse.set_program_name("kpsewhich")
if not release_date then
  dofile(kpse.lookup("l3build.lua"))
end
