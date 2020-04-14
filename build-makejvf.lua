local elu = require("build-elu.lua")

makejvfdir = makejvfdir or "./build/makejvf"
zvpfiledir = zvpfiledir or "./zvp"
vffiledir  = vffiledir  or "./vf"
tfmfiledir = tfmfiledir or "./tfm"

local jlreq_prefix_list = {
  "jlreq",
  "bjlreq",
  "zjlreq",
  "bzjlreq",
}
local font_series_list = {
  {"minl","ml"},
  {"minr","mr"},
  {"minb","mb"},
  {"gothr","gr"},
  {"gothb","gb"},
  {"gotheb","ge"},
  {"mgothr","mgr"},
}

local function jfmutil_zvp2vf(dir,in_zvp)
  dir = dir or "."
  -- print("> jfmutil zvp2vf " .. in_zvp)
  run(
    dir,
    "jfmutil zvp2vf " .. in_zvp
  )
end

local function generate_zvp(srcpath,dstpath,table)
  local src = assert(io.open(srcpath, "r"))
  local data = src:read("*all")
  src:close()
  local e = elu.new(data)
  local dst = assert(io.open(dstpath, "w"))
  dst:write(elu.result(e, table))
  assert(dst:close())
end

local function make_vf_all(srcdir,dstdir)
  for _,p in pairs(jlreq_prefix_list) do
    for _,s in pairs(font_series_list) do
      for _,u in ipairs({ "", "up" }) do
        for _,e in ipairs({ "nml", "exp" }) do
          for _,n in ipairs({ "", "n" }) do
            for _,v in ipairs({"-h","-v"}) do
              local eluname = p .. "--" .. u .. "template" .. v
              local zvpname = p .. "--" .. u .. e .. s[1] .. n .. v
              local elufile = eluname .. ".zvp.elu"
              local zvpfile = zvpname .. ".zvp"
              local elupath = srcdir .. "/" .. elufile
              local zvppath = dstdir .. "/" .. zvpfile
              local t = {}
              t.shape = s[1]
              t.cid_shape = s[2]
              t.is_expert = e == "exp"
              t.is_jis2004 = n == "n"
              t.jis2004_n = n
              print("Genarating "..zvpname.." ...")
              generate_zvp(elupath,zvppath,t)
              jfmutil_zvp2vf(dstdir,zvpfile)
            end
          end
        end
      end
    end
  end
end

function makejvf()
  cleandir(makejvfdir)
  make_vf_all(zvpfiledir,makejvfdir)
  vfname  = "*.vf"
  tfmname = "*.tfm"
  rm(vffiledir,vfname)
  rm(tfmfiledir,tfmname)
  cp(vfname,makejvfdir,vffiledir)
  cp(tfmname,makejvfdir,tfmfiledir)
end
