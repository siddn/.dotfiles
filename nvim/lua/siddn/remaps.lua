local augroup = vim.api.nvim_create_augroup
local highlight_group = augroup("SN.remaps_highlight-group", { clear = true })



-- Disabled
vim.keymap.set("n", "Q", "<nop>", { desc = "<Nop>" })


-- Explorer
vim.keymap.set("n", "<leader>pv", vim.cmd.Ex, { desc = "Explorer" })


-- Movements
vim.keymap.set("v", "J", ":m '>+1<CR>gv=gv",    { desc = "Move line down" })
vim.keymap.set("v", "K", ":m '<-2<CR>gv=gv",    { desc = "Move line up" })
vim.keymap.set("n", "J", function() -- "mzJ`z"
    local saved_pos = vim.fn.getpos(".")
    vim.cmd(":normal! J")
    vim.fn.setpos(".", saved_pos)
end, { desc = "J does not move cursor" })


-- Jumps
vim.keymap.set("n", "<C-d>", "<C-d>zz", { desc = "Center on half-page jumps" })
vim.keymap.set("n", "<C-u>", "<C-u>zz", { desc = "Center on half-page jumps" })
vim.keymap.set("n", "n", "nzzzv",       { desc = "Center on search jumps"})
vim.keymap.set("n", "N", "Nzzzv",       { desc = "Center on search jumps" })


-- Highlights
vim.keymap.set("n", "<leader>/h", vim.cmd.noh, { desc = "Clear highlights" })
vim.api.nvim_create_autocmd("TextYankPost", {
    desc = "Highlight when yanking text",
    group = highlight_group,
    callback = function()
        vim.highlight.on_yank()
    end,
})


-- Yanks
vim.keymap.set("n", "yY",         [[:%y<CR>]],  { desc = "Yank entire file" })
vim.keymap.set("n", "<leader>yY", [[:%y+<CR>]], { desc = "Yank entire file to clipboard" })
vim.keymap.set("n", "<leader>y",  [["+y]],      { desc = "Yank to clipboard" })
vim.keymap.set("v", "<leader>y",  [["+y]],      { desc = "Yank to clipboard" })
vim.keymap.set("n", "<leader>Y",  [["+yg_]],    { desc = "Yank to clipboard" })


-- Deletes
vim.keymap.set("n", "<leader>d", [["_d]],   { desc = "Don't save deleted text to buffer" })
vim.keymap.set("v", "<leader>d", [["_d]],   { desc = "Don't save deleted text to buffer" })
vim.keymap.set("x", "<leader>p", [["_dP]],  { desc = "Don't save deleted text to buffer" })


-- Text replace
vim.keymap.set("n", "<leader>s", [[:%s/\<<C-r><C-w>\>/<C-r><C-w>/gI<Left><Left><Left>]], { desc = "Global text replace" })
vim.keymap.set("n", "<leader>S", [[:.s/\<<C-r><C-w>\>/<C-r><C-w>/gI<Left><Left><Left>]], { desc = "Line text replace" })


-- Editor
vim.keymap.set("n", "<leader>ew", function()
    vim.wo.wrap = not vim.wo.wrap
end, { desc = "Toggle line wrapping" })

vim.keymap.set("n", "<leader>er", function()
    vim.wo.nu = true
    vim.wo.relativenumber = not vim.wo.relativenumber
end, { desc = "Toggle relative line numbers" })

