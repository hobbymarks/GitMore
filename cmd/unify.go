/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
	"gopkg.in/ini.v1"
)

// unifyCmd represents the unify command
var unifyCmd = &cobra.Command{
	Use:   "unify",
	Short: "unify git directory name",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: func(cmd *cobra.Command, args []string) {
		inplace, err := cmd.Flags().GetBool("inplace")
		if err != nil {
			log.Fatal(err)
		}
		cfm, err := cmd.Flags().GetBool("confirm")
		if err != nil {
			log.Fatal(err)
		}
		dirs, err := AllGitDirs(args)
		if err != nil {
			log.Error(err)
			return
		}
		for _, gdir := range dirs {
			gr, err := DecodeGitConfig(filepath.Join(gdir, ".git/config"))
			if err != nil {
				log.Error(err)
			} else {
				if inplace {
					fmt.Printf("%s==>%s\n", gdir, gr)
				} else {
					fmt.Printf("%s-->%s\n", gdir, gr)
					if cfm {
						switch confirm() {
						case A, All:
							inplace = true
							fmt.Printf("%s==>%s\n", gdir, gr)
						case Y, Yes:
							fmt.Printf("%s==>%s\n", gdir, gr)
						case N, No:
							continue
						case Q, Quit:
							os.Exit(0)
						}
					}
				}
			}
		}
	},
}

func init() {
	rootCmd.AddCommand(unifyCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// unifyCmd.PersistentFlags().String("foo", "", "A help for foo")

	unifyCmd.Flags().BoolP("confirm", "c", false, "Confirm unify git direcotry name")
	unifyCmd.Flags().BoolP("inplace", "i", false, "Unify git direcotry name inplace")
}

func DecodeGitConfig(configPath string) (string, error) {
	cfg, err := ini.Load(configPath)
	if err != nil {
		return "", err
	}

	// pattern := regexp.MustCompile(`(github.com/(?P<org>\S+)/(?P<repo>\S+).git)|(github.com/(?P<org>\S+)/(?P<repo>\S+))`)
	pattern := regexp.MustCompile(`(//(\S+)/(?P<org>\S+)/(?P<repo>\S+).git)|(//(\S+)/(?P<org>\S+)/(?P<repo>\S+))`)
	template := []byte("$repo@$org")
	result := []byte{}

	content := []byte(cfg.Section(`remote "origin"`).Key("url").String())
	for _, submatches := range pattern.FindAllSubmatchIndex(content, -1) {
		result = pattern.Expand(result, template, content, submatches)
	}
	log.Trace(string(result))

	return string(result), nil
}

func confirm() UserInput {
	var cmsg string

	fmt.Print("Please confirm (all,yes,no,quit):")
	fmt.Scan(&cmsg)

	return UserInput(strings.ToLower(cmsg))
}

type UserInput string

const (
	All  UserInput = "all"
	A    UserInput = "a"
	Yes  UserInput = "yes"
	Y    UserInput = "y"
	No   UserInput = "no"
	N    UserInput = "n"
	Quit UserInput = "quit"
	Q    UserInput = "q"
)
