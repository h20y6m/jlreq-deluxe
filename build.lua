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
tagfiles         = {"*.sty","*.tex","LICENSE"}
textfiles        = {"*.md", "LICENSE"}
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


-- Detail how to set the version automatically
function update_tag(file,content,tagname,tagdate)
  local author = "Yukimasa Morimi"
  if string.match(content,"Copyright %(c%)%s*(%d+)%S+ " .. author) then
    local year = os.date("%Y")
    content = string.gsub(content,
      "Copyright %(c%)%s*(%d+)%S+ " .. author,
      "Copyright (c) %1-" .. year .. " " .. author)
    content = string.gsub(content,year .. "-" .. year,year)
  end
  if string.match(file,"%.sty$") then
    content = string.gsub(content,
      "\n\\ProvidesExplPackage {([^}]+)} {%d%d%d%d%-%d%d%-%d%d} {%d+%.%d+%.%d+}",
      "\n\\ProvidesExplPackage {%1} {" .. tagdate .. "} {" .. tagname .. "}")
  end
  if string.match(file,"%.tex$") then
    return string.gsub(content,
      "\n\\date{%d%d%d%d%-%d%d%-%d%d}\n",
      "\n\\date{" .. tagdate .. "}\n")
  end
  return content
end


-- customize l3build internal functins
dofile("./build-customize.lua")
