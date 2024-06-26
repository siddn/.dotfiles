return {
    "neovim/nvim-lspconfig",
    dependencies = {
        "williamboman/mason.nvim",
        "williamboman/mason-lspconfig.nvim",
        "hrsh7th/cmp-nvim-lsp",
        "hrsh7th/cmp-buffer",
        "hrsh7th/cmp-path",
        "hrsh7th/cmp-cmdline",
        "hrsh7th/nvim-cmp",
        "L3MON4D3/LuaSnip",
        "saadparwaiz1/cmp_luasnip",
        "j-hui/fidget.nvim",
    },

    config = function()
        local cmp = require("cmp")
        local cmp_lsp = require("cmp_nvim_lsp")
        local capabilities = vim.tbl_deep_extend(
            "force",
            {},
            vim.lsp.protocol.make_client_capabilities(),
            cmp_lsp.default_capabilities())

        require("fidget").setup({})
        require("mason").setup()
        require("mason-lspconfig").setup({
            -- ensure_installed = {
            --     "dockerls",
            --     "bashls",
            --     "lua_ls",
            --     "pyright",
            --     "gopls", "templ",
            --     "clangd",
            --     "tsserver",
            -- },
            handlers = {
                function(server_name) -- default handler (optional)
                    require("lspconfig")[server_name].setup {
                        capabilities = capabilities
                    }
                end,
                ["basedpyright"] = function()
                    local lspconfig = require("lspconfig")
                    lspconfig.basedpyright.setup {
                        settings = {
                            basedpyright = {
                                analysis = {
                                    typeCheckingMode='strict' -- Set to either 'off', 'basic', 'standard', 'strict'
                                }
                            }
                        }
                    }
                    vim.api.nvim_create_user_command(
                        'PyTypeCheck',
                        function(opts)
                            local lspconfig = require("lspconfig")
                            lspconfig.basedpyright.setup {
                                settings = {
                                    basedpyright = {
                                        analysis = {
                                            typeCheckingMode=opts.args -- Set to either 'off', 'basic', 'standard', 'strict'
                                        }
                                    }
                                }
                            }
                        end,
                        { nargs = 1 }
                    )


                end,

                ["lua_ls"] = function()
                    local lspconfig = require("lspconfig")
                    lspconfig.lua_ls.setup {
                        capabilities = capabilities,
                        settings = {
                            Lua = {
                                runtime = { version = "Lua 5.1" },
                                diagnostics = {
                                    globals = { "vim", "it", "describe", "before_each", "after_each" },
                                }
                            }
                        }
                    }
                end,
            }
        })

        local cmp_select = { behavior = cmp.SelectBehavior.Select }

        cmp.setup({
            snippet = {
                expand = function(args)
                    require("luasnip").lsp_expand(args.body) -- For `luasnip` users.
                end,
            },
            mapping = cmp.mapping.preset.insert({
                ["<C-p>"] = cmp.mapping.select_prev_item(cmp_select),
                ["<C-n>"] = cmp.mapping.select_next_item(cmp_select),
                ["<C-y>"] = cmp.mapping.confirm({ select = true }),
                ["<C-l>"] = cmp.mapping.complete(),
            }),
            sources = cmp.config.sources({
                { name = "nvim_lsp" },
                { name = "luasnip" }, -- For luasnip users.
            }, {
                { name = "buffer" },
            })
        })

        vim.diagnostic.config({
            -- update_in_insert = true,
            float = {
                focusable = false,
                style = "minimal",
                border = "rounded",
                source = "always",
                header = "",
                prefix = "",
            },
        })


        -- LSP keybinds
        vim.api.nvim_create_autocmd("LspAttach", {
            callback = function(e)
                vim.keymap.set("n", "gd",           function() vim.lsp.buf.definition()         end, { buffer = e.buf, desc = "LSP Goto defintion" })
                vim.keymap.set("n", "gD",           function() vim.lsp.buf.declaration()        end, { buffer = e.buf, desc = "LSP Goto declaration" })
                vim.keymap.set("n", "gr",           function() vim.lsp.buf.references()         end, { buffer = e.buf, desc = "LSP Get references" })
                vim.keymap.set("n", "<leader>lca",  function() vim.lsp.buf.code_action()        end, { buffer = e.buf, desc = "LSP code action" })
                vim.keymap.set("n", "<leader>lrn",  function() vim.lsp.buf.rename()             end, { buffer = e.buf, desc = "LSP rename" })
                vim.keymap.set("n", "<leader>lws",  function() vim.lsp.buf.workspace_symbol()   end, { buffer = e.buf, desc = "LSP workspace symbol" })
                vim.keymap.set("n", "<leader>ld",   function() vim.diagnostic.open_float()      end, { buffer = e.buf, desc = "LSP open diagnostics" })
                vim.keymap.set("n", "[d",           function() vim.diagnostic.goto_prev()       end, { buffer = e.buf, desc = "LSP Goto prev diagnostic" })
                vim.keymap.set("n", "]d",           function() vim.diagnostic.goto_next()       end, { buffer = e.buf, desc = "LSP Goto next diagnostic" })
                vim.keymap.set("n", "K",            function() vim.lsp.buf.hover()              end, { buffer = e.buf, desc = "LSP display hover" })
                vim.keymap.set("n", "<C-p>",        function() vim.lsp.buf.signature_help()     end, { buffer = e.buf, desc = "LSP display signature help" })
                vim.keymap.set("i", "<C-p>",        function() vim.lsp.buf.signature_help()     end, { buffer = e.buf, desc = "LSP display signature help" })
                vim.keymap.set("v", "<C-p>",        function() vim.lsp.buf.signature_help()     end, { buffer = e.buf, desc = "LSP display signature help" })
            end
        })
    end
}

