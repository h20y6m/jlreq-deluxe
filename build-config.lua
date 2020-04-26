
dvipdfexe  = dvipdfexe or "dvipdfmx"
dvipdfopts = dvipdfopts or ""

function customize_dvitopdf(dvitopdf)
  return function(name, dir, engine, hide)
    local dir = dir or "."
    if fileexists(dir .. "/" .. name .. ".dvi") then
      return runcmd(dvipdfexe .. " " .. dvipdfopts .. " " .. name .. ".dvi", dir)
    end
    return 0
  end
end

function customize_typeset(typeset)
  return function(file,dir,exe)
    local errorlevel = typeset(file,dir,exe)
    if errorlevel ~= 0 then return errorlevel end

    local name = jobname(file)
    errorlevel = dvitopdf(name,dir)
    return errorlevel
  end
end

function customize_install_files(install_files)
  return function(target,full,dry_run)
    local errorlevel = install_files(target,full,dry_run)
    if errorlevel ~= 0 then return errorlevel end

    if dry_run then
      print(target .. "/fonts/vf/public/" .. ctanpkg)
      print(target .. "/fonts/tfm/public/" .. ctanpkg)
    else
      mkdir(target .. "/fonts/vf/public/" .. ctanpkg)
      mkdir(target .. "/fonts/tfm/public/" .. ctanpkg)
      errorlevel = cp("*.vf", maindir .. "/vf", target .. "/fonts/vf/public/" .. ctanpkg)
      if errorlevel ~= 0 then return errorlevel end
      errorlevel = cp("*.tfm", maindir .. "/tfm", target .. "/fonts/tfm/public/" .. ctanpkg)
      if errorlevel ~= 0 then return errorlevel end
    end

    return 0
  end
end

function customize_copyctan(copyctan)
  return function()
    copyctan()
    mkdir(ctandir .. "/" .. ctanpkg .. "/vf")
    mkdir(ctandir .. "/" .. ctanpkg .. "/tfm")
    cp("*.vf", maindir .. "/vf", ctandir .. "/" .. ctanpkg .. "/vf")
    cp("*.tfm", maindir .. "/tfm", ctandir .. "/" .. ctanpkg .. "/tfm")
  end
end
