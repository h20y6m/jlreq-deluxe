function mkdir(dir)
  if os.type == "windows" then
    dir = string.gsub(dir,"/","\\")
    return os.execute("if not exist " .. dir .. " mkdir " .. dir)
  else
    return os.execute("mkdir -p " .. dir)
  end
end

function rm(dir,file)
  if os.type == "windows" then
    dir = string.gsub(dir,"/","\\")
    return os.execute("del /q " .. dir .. "\\" .. file)
  else
    return os.execute("rm -f " .. dir .. "/" .. file)
  end
end

function cp(file,src,dest)
  if os.type == "windows" then
    src = string.gsub(src,"/","\\")
    dest = string.gsub(dest,"/","\\")
    return os.execute("copy /b /y " .. src .. "\\" .. file .. " " .. dest .. "\\")
  else
    return os.execute("cp -f " .. src .. "/" .. file .. " " .. dest .. "/")
  end
end

function run(dir,cmd)
  if os.type == "windows" then
    dir = string.gsub(dir,"/","\\")
    return os.execute("cd " .. dir .. " & " .. cmd)
  else
    return os.execute("cd " .. dir .. "; " .. cmd)
  end
end
