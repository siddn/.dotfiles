return {
    "nvim-telescope/telescope.nvim",
    tag = "0.1.8",
    dependencies = {
        "nvim-lua/plenary.nvim",
    },

    config = function()
        require("telescope").setup{
            defaults = {
                file_ignore_patterns = {
                    "%.git$",
                    "venv",
                    "node_modules",
                },
            },
        }
        local builtin = require("telescope.builtin")


        -- Git file search
        vim.keymap.set("n", "<leader>/g", builtin.git_files, { desc = "Find git files" })


        -- File search
        vim.keymap.set("n", "<leader>/f", builtin.find_files, { desc = "Find files" })
        vim.keymap.set("n", "<leader>/F", function()
            builtin.find_files({
                hidden = true,
                no_ignore = true,
            })
        end, { desc = "Find files (including hidden)" })


        -- Grep search
        vim.keymap.set("n", "<leader>/s", function()
            vim.ui.input({ prompt = "Grep > " }, function(input)
                if not input then
                    return
                end
                builtin.grep_string({ search = input })
            end)
        end, { desc = "Grep search" })

        vim.keymap.set("n", "<leader>/S", function()
            builtin.live_grep()
        end, { desc = "Live Grep search" })


        -- Theme search
        vim.keymap.set("n", "<leader>/c", function()
            builtin.colorscheme({
                enable_preview = true,
                layout_config = {
                    preview_cutoff = 0,
                    width = 0.9,
                    horizontal = {
                        preview_width = 0.70,
                    },
                },
            })
        end, { desc = "Search colorschemes" })


        -- Vim search
        vim.keymap.set("n", "<leader>/vh", builtin.help_tags,   { desc = "Search vim help" })
        vim.keymap.set("n", "<leader>/vk", builtin.keymaps,     { desc = "Search vim keymaps" })
    end
}

