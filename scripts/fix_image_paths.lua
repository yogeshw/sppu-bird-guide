function Image(img)
    -- Extract filename from path
    local filename = img.src:match("[^/]*$") or img.src
    img.src = "images/" .. filename:gsub("^%./", ""):gsub("^../images/", "")
    return img
end

function RawBlock(raw)
    if raw.format == "tex" then
        -- Handle \birdentry command
        local pattern = "\\birdentry{(.-)}{(.-)}{(.-)}{(.-)}{(.-)}{(.-)}{(.-)}{(.-)}{(.-)}"
        local name, latin, size, status, field, best, habits, nesting, image = raw.text:match(pattern)
        
        if name then
            -- Create HTML structure for bird entry
            local html = string.format([[
                <div class="bird-entry">
                    <div class="bird-image">
                        <img src="images/%s" alt="%s" class="bird-photo">
                    </div>
                    <div class="bird-info">
                        <h3>%s <em>(%s)</em></h3>
                        <p><strong>Size:</strong> %s</p>
                        <p><strong>Status:</strong> %s</p>
                        <p><strong>Field characters:</strong> %s</p>
                        <p><strong>Best seen at:</strong> %s</p>
                        <p><strong>Habits:</strong> %s</p>
                        <p><strong>Nesting:</strong> %s</p>
                    </div>
                </div>
            ]], image, name, name, latin, size, status, field, best, habits, nesting)
            
            return pandoc.RawBlock('html', html)
        end
    end
    return nil
end

-- Return the table of filter functions
return {
    Image = Image,
    RawBlock = RawBlock
}
