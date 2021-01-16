local elu = require("build-elu.lua")

makejvfdir = makejvfdir or "./build/makejvf"
zvpfiledir = zvpfiledir or "./zvp"
vffiledir  = vffiledir  or "./vf"
tfmfiledir = tfmfiledir or "./tfm"

local font_series_list = {
  {"minl","ml"},
  {"minr","mr"},
  {"minb","mb"},
  {"gothr","gr"},
  {"gothb","gb"},
  {"gotheb","ge"},
  {"mgothr","mgr"},
}

local function jfmutil_zvp02vf(dir,in_zvp0)
  dir = dir or "."
  run(
    dir,
    "jfmutil zvp02vf " .. in_zvp0
  )
end

local function jfmutil_zpl2tfm(dir,in_zpl)
  dir = dir or "."
  run(
    dir,
    "jfmutil zpl2tfm " .. in_zpl
  )
end

local function jfmutil_compact(dir,in_vf,out_vf)
  dir = dir or "."
  run(
    dir,
    "jfmutil compact " .. in_vf .. " " .. out_vf
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

local function kpairs(tbl)
  local keys = {}
  for k in pairs(tbl) do keys[#keys+1] = k end
  table.sort(keys)
  local i = 0
  return function ()
    i = i + 1
    return keys[i], tbl[keys[i]]
  end
end

local function make_vf_all(srcdir,dstdir)
  for _,b in ipairs({ "", "b" }) do
    for _,z in ipairs({ "", "z" }) do
      for _,u in ipairs({ "", "up" }) do
        for _,e in ipairs({ "nml", "exp" }) do
          for _,s in pairs(font_series_list) do
            for _,n in ipairs({ "", "n" }) do
              for _,v in ipairs({"-h","-v"}) do
                local zvpeluname = "jlreq--" .. u .. "template" .. v
                local zpleluname = "jlreq--" .. u .. "template" .. v
                local vfname = b .. z .. "jlreq--" .. u .. e .. s[1] .. n .. v
                local zvpelufile = zvpeluname .. ".zvp0.elu"
                local zplelufile = zpleluname .. ".zpl.elu"
                local zvpfile = vfname .. ".zvp0"
                local zplfile = vfname .. ".zpl"
                local zvpelupath = srcdir .. "/" .. zvpelufile
                local zplelupath = srcdir .. "/" .. zplelufile
                local zvppath = dstdir .. "/" .. zvpfile
                local zplpath = dstdir .. "/" .. zplfile
                local t = {}
                t.kpairs = kpairs
                t.shape = s[1]
                t.cid_shape = s[2]
                t.is_burasage = b == "b"
                t.is_zenkakunibu = z == "z"
                t.is_expert = e == "exp"
                t.is_jis2004 = n == "n"
                t.jis2004_n = n
                print("Genarating "..vfname.." ...")
                generate_zvp(zvpelupath,zvppath,t)
                generate_zvp(zplelupath,zplpath,t)
                jfmutil_zvp02vf(dstdir,zvpfile)
                jfmutil_zpl2tfm(dstdir,zplfile)
              end
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
