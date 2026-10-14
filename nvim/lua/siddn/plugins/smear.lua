return {
    "sphamba/smear-cursor.nvim",

    config = function()
        require("smear_cursor").setup({
            time_interval = 10,
            stiffness = 0.9,
            trailing_stiffness = 0.5,
            distance_stop_animation = 0.5,
        })

        vim.keymap.set("n", "<leader>es", "<cmd>SmearCursorToggle<CR>", { desc = "Toggle Smear" })
    end
}
