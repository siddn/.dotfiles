local augroup = vim.api.nvim_create_augroup
local all_files_group = augroup("SN.files_all-group", { clear = true })



vim.filetype.add({
    filename = {
        [".dockerignore"] = "gitignore",
    },
    pattern = {
        ["*%.env.*"]        = "sh",
        [".*%.gitignore$"]  = "gitignore",
        [".*%.ignore$"]     = "gitignore",
        [".*Dockerfile.*"]  = "dockerfile",
    },
})


-- All files
vim.api.nvim_create_autocmd("BufWritePre", {
    desc = "Remove trailing whitespace from files",
    group = all_files_group,
    pattern = "*",
    command = [[%s/\s\+$//e]],
})

